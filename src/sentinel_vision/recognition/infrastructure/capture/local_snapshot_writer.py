from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.infrastructure.paths import safe_subject_id

_MARGIN = 0.3


class SnapshotWriteError(RuntimeError):
    pass


class LocalSnapshotWriter:
    def __init__(self, root: Path, camera_name: str) -> None:
        self._root = root
        self._camera = safe_subject_id(camera_name) if camera_name.strip() else "cam"

    def save(
        self, frame: np.ndarray, observation: FaceObservation, subject_label: str, score: float
    ) -> Path:
        subject_dir = self._root / safe_subject_id(subject_label)
        subject_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S_%f")[:-3]
        path = subject_dir / f"{stamp}_{self._camera}_{score:.2f}.jpg"
        if not cv2.imwrite(str(path), _crop(frame, observation)):
            raise SnapshotWriteError(f"failed to write snapshot: {path}")
        return path


def _crop(frame: np.ndarray, observation: FaceObservation) -> np.ndarray:
    height, width = frame.shape[:2]
    margin_x = int(observation.width * _MARGIN)
    margin_y = int(observation.height * _MARGIN)
    x1 = max(0, observation.x1 - margin_x)
    y1 = max(0, observation.y1 - margin_y)
    x2 = min(width, observation.x2 + margin_x)
    y2 = min(height, observation.y2 + margin_y)
    return frame[y1:y2, x1:x2]
