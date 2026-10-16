from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult

_Box = tuple[int, int, int, int]


class PlateSnapshotWriter(Protocol):
    def save(self, frame: np.ndarray, box: _Box, plate_value: str) -> Path: ...


class PlateSnapshotSink:
    def __init__(self, writer: PlateSnapshotWriter) -> None:
        self._writer = writer

    def on_watched(self, frame: np.ndarray, box: _Box, result: PlateRecognitionResult) -> None:
        if result.plate is not None:
            self._writer.save(frame, box, result.plate.value)
