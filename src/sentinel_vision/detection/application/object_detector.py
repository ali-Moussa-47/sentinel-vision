from __future__ import annotations

from typing import Protocol

import numpy as np

from sentinel_vision.detection.domain.detected_object import DetectedObject


class ObjectDetectionError(RuntimeError):
    pass


class ObjectDetector(Protocol):
    def detect(self, frame: np.ndarray) -> list[DetectedObject]: ...
