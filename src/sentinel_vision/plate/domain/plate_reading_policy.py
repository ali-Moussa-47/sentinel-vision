from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.plate.domain.plate_reading import PlateReading
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist


@dataclass(frozen=True)
class PlateReadingPolicy:
    min_confidence: float

    def evaluate(self, reading: PlateReading, watchlist: PlateWatchlist) -> PlateRecognitionResult:
        if reading.confidence < self.min_confidence:
            return PlateRecognitionResult.low_confidence(reading.confidence)
        if watchlist.contains(reading.plate):
            return PlateRecognitionResult.watched(reading.plate, reading.confidence)
        return PlateRecognitionResult.seen(reading.plate, reading.confidence)
