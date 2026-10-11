from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import cv2
import numpy as np

from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.config import AppConfig
from sentinel_vision.recognition.application.enroll_subject import EnrollmentError, EnrollSubject
from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace, FaceAnalysisError
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.infrastructure.vision.insightface_face_analyzer import (
    FaceAnalyzerInitializationError,
    InsightFaceFaceAnalyzer,
)
from sentinel_vision.recognition.infrastructure.watchlist.local_watchlist_writer import (
    LocalWatchlistWriter,
)

_CAPTURE_KEY = 32
_CANCEL_KEY = 27

_READY = (106, 187, 102)
_MUTED = (141, 129, 119)
_TEXT = (250, 247, 245)
_PANEL = (16, 20, 17)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_BANNER_H = 40


def enroll() -> None:
    parser = argparse.ArgumentParser(prog="sentinel-vision-enroll")
    parser.add_argument("label", help="display name of the consented subject")
    parser.add_argument("--camera", type=int, help="camera index (default 0)")
    parser.add_argument(
        "--source", help="RTSP/stream URL (overrides --camera; or env SENTINEL_CAMERA_URL)"
    )
    arguments = parser.parse_args()
    config = resolve_camera_config(AppConfig(), arguments.camera, arguments.source)
    try:
        _run_enrollment(arguments.label, config)
    except (CameraError, FaceAnalyzerInitializationError, FaceAnalysisError) as error:
        print(f"Enrollment could not start: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("\nStopped.")


def _run_enrollment(label: str, config: AppConfig) -> None:
    warnings.filterwarnings("ignore", message="`estimate` is deprecated", category=FutureWarning)

    print("Loading recognition model (first run downloads it)...")
    analyzer = InsightFaceFaceAnalyzer(config)
    quality_gate = FaceQualityGate(config.min_face_pixels, config.min_detection_score)
    enroller = EnrollSubject(LocalWatchlistWriter(Path(config.watchlist_path)), quality_gate)

    window = f"{config.window_title} - Enroll {label}"
    with open_frame_source(config) as camera:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        while True:
            frame = camera.read()
            faces = analyzer.analyze(frame)

            preview = frame.copy()
            _draw_enrollment(preview, faces, label, quality_gate)
            cv2.imshow(window, preview)

            key = cv2.waitKey(1) & 0xFF
            if key == _CANCEL_KEY:
                break
            if key == _CAPTURE_KEY:
                _capture(enroller, label, frame, faces)
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break

    cv2.destroyAllWindows()


def _capture(
    enroller: EnrollSubject, label: str, frame: np.ndarray, faces: list[AnalyzedFace]
) -> None:
    try:
        path = enroller.enroll(label, frame, faces)
    except EnrollmentError as error:
        print(f"Capture rejected: {error}")
        return
    except (OSError, ValueError) as error:
        print(f"Capture failed: {error}")
        return
    print(f"Saved reference: {path.name}")


def _draw_enrollment(
    frame: np.ndarray,
    faces: list[AnalyzedFace],
    label: str,
    quality_gate: FaceQualityGate,
) -> None:
    ready = len(faces) == 1 and quality_gate.is_reliable(faces[0].observation)
    color = _READY if ready else _MUTED
    for face in faces:
        box = face.observation
        cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), color, 2)

    width = frame.shape[1]
    cv2.rectangle(frame, (0, 0), (width, _BANNER_H), _PANEL, -1)
    cv2.putText(frame, f"ENROLL   {label}", (16, 27), _FONT, 0.6, _TEXT, 1, cv2.LINE_AA)

    if ready:
        hint = "SPACE capture    ESC cancel"
    elif len(faces) == 1:
        hint = "move closer - face not eligible"
    else:
        hint = f"{len(faces)} faces - show exactly one"
    (hint_width, _), _ = cv2.getTextSize(hint, _FONT, 0.5, 1)
    cv2.putText(frame, hint, (width - hint_width - 16, 26), _FONT, 0.5, color, 1, cv2.LINE_AA)


if __name__ == "__main__":
    enroll()
