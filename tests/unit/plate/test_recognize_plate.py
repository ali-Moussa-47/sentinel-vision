from __future__ import annotations

import numpy as np

from sentinel_vision.plate.application.plate_reader import AnalyzedPlate
from sentinel_vision.plate.application.recognize_plate import RecognizePlate
from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_reading import PlateReading
from sentinel_vision.plate.domain.plate_reading_policy import PlateReadingPolicy
from sentinel_vision.plate.domain.plate_recognition_result import PlateDecision
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist

_FRAME = np.zeros((4, 4, 3), dtype=np.uint8)


class _FakeReader:
    def __init__(self, plates: list[AnalyzedPlate]) -> None:
        self._plates = plates

    def read(self, frame: np.ndarray) -> list[AnalyzedPlate]:
        return self._plates


def _plate(value: str, confidence: float) -> AnalyzedPlate:
    return AnalyzedPlate(0, 0, 10, 10, PlateReading(PlateNumber.normalize(value), confidence))


def test_each_plate_is_evaluated_against_the_watchlist() -> None:
    reader = _FakeReader([_plate("ab123cd", 0.9), _plate("zz999", 0.9)])
    recognize = RecognizePlate(reader, PlateWatchlist.of(["AB123CD"]), PlateReadingPolicy(0.6))
    results = recognize(_FRAME)
    assert [r.result.decision for r in results] == [PlateDecision.WATCHED, PlateDecision.SEEN]


def test_locations_are_preserved() -> None:
    reader = _FakeReader([_plate("ab123cd", 0.9)])
    recognize = RecognizePlate(reader, PlateWatchlist.of([]), PlateReadingPolicy(0.6))
    [plate] = recognize(_FRAME)
    assert (plate.x1, plate.y1, plate.x2, plate.y2) == (0, 0, 10, 10)
