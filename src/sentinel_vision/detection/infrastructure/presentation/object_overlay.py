from __future__ import annotations

import cv2
import numpy as np

from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.domain.tracked_object import TrackedObject

_PERSON = (106, 187, 102)
_VEHICLE = (246, 181, 100)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_SCALE = 0.5


def draw(frame: np.ndarray, objects: list[DetectedObject]) -> None:
    for obj in objects:
        _draw_box(frame, obj, f"{obj.label} {obj.score:.2f}")


def draw_tracked(frame: np.ndarray, tracked: list[TrackedObject]) -> None:
    for item in tracked:
        obj = item.observation
        _draw_box(frame, obj, f"#{item.track_id} {obj.label} {obj.score:.2f}")


def _draw_box(frame: np.ndarray, obj: DetectedObject, label: str) -> None:
    color = _PERSON if obj.label == "person" else _VEHICLE
    cv2.rectangle(frame, (obj.x1, obj.y1), (obj.x2, obj.y2), color, 2, cv2.LINE_AA)
    cv2.putText(frame, label, (obj.x1, max(18, obj.y1 - 8)), _FONT, _SCALE, color, 1, cv2.LINE_AA)
