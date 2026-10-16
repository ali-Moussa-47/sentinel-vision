from __future__ import annotations

import argparse
import time
from dataclasses import replace

import cv2
import numpy as np

from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.config import AppConfig
from sentinel_vision.detection.application.object_detector import ObjectDetectionError
from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.infrastructure.presentation import object_overlay
from sentinel_vision.detection.infrastructure.yolox_onnx_detector import YoloxOnnxObjectDetector

_TEXT = (250, 247, 245)
_PANEL = (16, 20, 17)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_BANNER_H = 40
_QUIT_KEYS = {ord("q"), 27}


def probe() -> None:
    parser = argparse.ArgumentParser(prog="sentinel-vision-detect")
    parser.add_argument("--camera", type=int, help="camera index")
    parser.add_argument("--source", help="RTSP/stream URL (or env SENTINEL_CAMERA_URL)")
    parser.add_argument("--model", help="path to a YOLOX .onnx model")
    parser.add_argument("--score", type=float, help="minimum detection score")
    arguments = parser.parse_args()
    try:
        _run_probe(_config_from(arguments))
    except (CameraError, ObjectDetectionError, FileNotFoundError) as error:
        print(f"Object probe could not run: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("\nStopped.")


def _config_from(arguments: argparse.Namespace) -> AppConfig:
    config = resolve_camera_config(AppConfig(), arguments.camera, arguments.source)
    if arguments.model is not None:
        config = replace(config, detection_model_path=arguments.model)
    if arguments.score is not None:
        config = replace(config, detection_score_threshold=arguments.score)
    return config


def _run_probe(config: AppConfig) -> None:
    detector = YoloxOnnxObjectDetector(
        config.detection_model_path,
        config.detection_score_threshold,
        config.detection_nms_threshold,
        config.providers,
    )
    window = f"{config.window_title} - Object probe"
    fps = 0.0
    with open_frame_source(config) as camera:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        while True:
            start = time.perf_counter()
            frame = camera.read()
            objects = detector.detect(frame)
            _draw(frame, objects, fps, config)
            cv2.imshow(window, frame)
            if cv2.waitKey(1) & 0xFF in _QUIT_KEYS:
                break
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break
            elapsed = time.perf_counter() - start
            if elapsed > 0:
                fps = (0.9 * fps + 0.1 / elapsed) if fps else 1.0 / elapsed
    cv2.destroyAllWindows()


def _draw(frame: np.ndarray, objects: list[DetectedObject], fps: float, config: AppConfig) -> None:
    object_overlay.draw(frame, objects)
    _draw_banner(frame, objects, fps, config)


def _draw_banner(
    frame: np.ndarray, objects: list[DetectedObject], fps: float, config: AppConfig
) -> None:
    height, width = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (width, _BANNER_H), _PANEL, -1)
    model = config.detection_model_path.rsplit("/", 1)[-1]
    left = f"{width}x{height}   {model}   score>={config.detection_score_threshold:.2f}   {fps:4.1f} FPS"
    cv2.putText(frame, left, (16, 26), _FONT, 0.55, _TEXT, 1, cv2.LINE_AA)
    right = f"{len(objects)} objects" if objects else "no object"
    (text_width, _), _ = cv2.getTextSize(right, _FONT, 0.55, 1)
    cv2.putText(frame, right, (width - text_width - 16, 26), _FONT, 0.55, _TEXT, 1, cv2.LINE_AA)


if __name__ == "__main__":
    probe()
