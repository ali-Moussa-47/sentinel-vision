from __future__ import annotations

import cv2
import numpy as np

from sentinel_vision.plate.domain.plate_recognition_result import (
    PlateDecision,
    PlateRecognitionResult,
)

_Box = tuple[int, int, int, int]
_WATCHED = (80, 83, 239)
_SEEN = (194, 183, 174)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_SCALE = 0.5


def draw_on_vehicles(frame: np.ndarray, entries: list[tuple[_Box, PlateRecognitionResult]]) -> None:
    height = frame.shape[0]
    for box, result in entries:
        color, label = _appearance(result)
        baseline = min(box[3] + 20, height - 6)
        cv2.putText(frame, label, (box[0], baseline), _FONT, _SCALE, color, 1, cv2.LINE_AA)


def _appearance(result: PlateRecognitionResult) -> tuple[tuple[int, int, int], str]:
    if result.plate is None:
        return _SEEN, "PLATE?"
    if result.decision is PlateDecision.WATCHED:
        return _WATCHED, f"WATCHED {result.plate.value}"
    return _SEEN, f"PLATE {result.plate.value}"
