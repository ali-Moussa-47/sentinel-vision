from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sentinel_vision.plate.application.plate_reader import PlateReader
from sentinel_vision.plate.domain.plate_reading_policy import PlateReadingPolicy
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist


@dataclass(frozen=True)
class RecognizedPlate:
    x1: int
    y1: int
    x2: int
    y2: int
    result: PlateRecognitionResult


class RecognizePlate:
    def __init__(
        self, reader: PlateReader, watchlist: PlateWatchlist, policy: PlateReadingPolicy
    ) -> None:
        self._reader = reader
        self._watchlist = watchlist
        self._policy = policy

    def __call__(self, frame: np.ndarray) -> list[RecognizedPlate]:
        plates = self._reader.read(frame)
        return [
            RecognizedPlate(
                plate.x1, plate.y1, plate.x2, plate.y2,
                self._policy.evaluate(plate.reading, self._watchlist),
            )
            for plate in plates
        ]
