from __future__ import annotations

import argparse
import time
import warnings
from dataclasses import replace

import cv2
import numpy as np

from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.config import AppConfig
from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace, FaceAnalysisError
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.infrastructure.vision.insightface_face_analyzer import (
    FaceAnalyzerInitializationError,
    InsightFaceFaceAnalyzer,
)

_RELIABLE = (106, 187, 102)
_DETECT_ONLY = (246, 181, 100)
_TEXT = (250, 247, 245)
_PANEL = (16, 20, 17)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_BANNER_H = 40
_QUIT_KEYS = {ord("q"), 27}


def probe() -> None:
    parser = argparse.ArgumentParser(prog="sentinel-vision-probe")
    parser.add_argument("--camera", type=int, help="camera index")
    parser.add_argument(
        "--source", help="RTSP/stream URL (overrides --camera; or env SENTINEL_CAMERA_URL)"
    )
    parser.add_argument("--width", type=int, help="requested capture width")
    parser.add_argument("--height", type=int, help="requested capture height")
    parser.add_argument("--det-size", type=int, help="square detector input, e.g. 640 or 960")
    arguments = parser.parse_args()
    try:
        _run_probe(_config_from(arguments))
    except (CameraError, FaceAnalyzerInitializationError, FaceAnalysisError) as error:
        print(f"Distance probe could not run: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("\nStopped.")


def _config_from(arguments: argparse.Namespace) -> AppConfig:
    config = resolve_camera_config(AppConfig(), arguments.camera, arguments.source)
    if arguments.width is not None:
        config = replace(config, frame_width=arguments.width)
    if arguments.height is not None:
        config = replace(config, frame_height=arguments.height)
    if arguments.det_size is not None:
        config = replace(config, det_size=(arguments.det_size, arguments.det_size))
    return config


def _run_probe(config: AppConfig) -> None:
    warnings.filterwarnings("ignore", message="`estimate` is deprecated", category=FutureWarning)
    print("Loading recognition model (first run downloads it)...")
    analyzer = InsightFaceFaceAnalyzer(config)
    quality_gate = FaceQualityGate(config.min_face_pixels, config.min_detection_score)

    window = f"{config.window_title} - Distance probe"
    fps = 0.0
    with open_frame_source(config) as camera:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        while True:
            start = time.perf_counter()

            frame = camera.read()
            faces = analyzer.analyze(frame)
            _draw(frame, faces, quality_gate, fps, config)
            cv2.imshow(window, frame)

            if cv2.waitKey(1) & 0xFF in _QUIT_KEYS:
                break
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break

            elapsed = time.perf_counter() - start
            if elapsed > 0:
                fps = (0.9 * fps + 0.1 / elapsed) if fps else 1.0 / elapsed

    cv2.destroyAllWindows()


def _min_side(face: AnalyzedFace) -> int:
    return min(face.observation.width, face.observation.height)


def _draw(
    frame: np.ndarray,
    faces: list[AnalyzedFace],
    quality_gate: FaceQualityGate,
    fps: float,
    config: AppConfig,
) -> None:
    for face in faces:
        _draw_face(frame, face, quality_gate)
    _draw_banner(frame, faces, quality_gate, fps, config)


def _draw_face(frame: np.ndarray, face: AnalyzedFace, quality_gate: FaceQualityGate) -> None:
    box = face.observation
    reliable = quality_gate.is_reliable(box)
    color = _RELIABLE if reliable else _DETECT_ONLY
    cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), color, 2)
    tag = "SIZE OK" if reliable else "TOO SMALL"
    label = f"{_min_side(face)}px   det {box.detection_score:.2f}   {tag}"
    cv2.putText(frame, label, (box.x1, max(18, box.y1 - 8)), _FONT, 0.5, color, 1, cv2.LINE_AA)


def _draw_banner(
    frame: np.ndarray,
    faces: list[AnalyzedFace],
    quality_gate: FaceQualityGate,
    fps: float,
    config: AppConfig,
) -> None:
    height, width = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (width, _BANNER_H), _PANEL, -1)
    left = (
        f"{width}x{height}   det {config.det_size[0]}   "
        f"size>={config.min_face_pixels}px   {fps:4.1f} FPS"
    )
    cv2.putText(frame, left, (16, 26), _FONT, 0.55, _TEXT, 1, cv2.LINE_AA)

    if faces:
        largest = max(faces, key=_min_side)
        reliable = quality_gate.is_reliable(largest.observation)
        right = f"largest {_min_side(largest)}px   {'SIZE OK' if reliable else 'too small'}"
    else:
        right = "no face"
    (text_width, _), _ = cv2.getTextSize(right, _FONT, 0.55, 1)
    cv2.putText(frame, right, (width - text_width - 16, 26), _FONT, 0.55, _TEXT, 1, cv2.LINE_AA)


if __name__ == "__main__":
    probe()
