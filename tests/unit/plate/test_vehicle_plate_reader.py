from __future__ import annotations

import numpy as np

from sentinel_vision.plate.application.plate_reader import AnalyzedPlate
from sentinel_vision.plate.application.recognize_plate import RecognizePlate
from sentinel_vision.plate.application.vehicle_plate_reader import VehiclePlateReader
from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_reading import PlateReading
from sentinel_vision.plate.domain.plate_reading_policy import PlateReadingPolicy
from sentinel_vision.plate.domain.plate_recognition_result import PlateDecision
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist

_CROP = np.zeros((10, 10, 3), dtype=np.uint8)


class _ConstantReader:
    def __init__(self, plate_value: str) -> None:
        self._plate_value = plate_value
        self.calls = 0

    def read(self, frame: np.ndarray) -> list[AnalyzedPlate]:
        self.calls += 1
        return [_analyzed(self._plate_value)]


class _CyclingReader:
    def __init__(self) -> None:
        self.calls = 0

    def read(self, frame: np.ndarray) -> list[AnalyzedPlate]:
        self.calls += 1
        return [_analyzed(f"AB{self.calls}")]


def _analyzed(value: str) -> AnalyzedPlate:
    return AnalyzedPlate(0, 0, 10, 10, PlateReading(PlateNumber.normalize(value), 0.9))


def _vehicle_reader(
    reader: object, watch: bool, burst: int = 8, interval: int = 3, confirm: int = 2
) -> VehiclePlateReader:
    watchlist = PlateWatchlist.of(["AB123"] if watch else [])
    recognize = RecognizePlate(reader, watchlist, PlateReadingPolicy(0.6))
    return VehiclePlateReader(recognize, burst, interval, confirm, window=5)


def test_consistent_plate_is_confirmed_quickly_during_the_burst() -> None:
    reader = _vehicle_reader(_ConstantReader("AB123"), watch=True)
    assert reader.update([(1, _CROP)]) == {}
    confirmed = reader.update([(1, _CROP)])
    assert confirmed[1].decision is PlateDecision.WATCHED
    assert confirmed[1].plate == PlateNumber("AB123")


def test_unconfirmed_vehicle_is_read_every_frame_during_the_burst() -> None:
    counting = _CyclingReader()
    reader = _vehicle_reader(counting, watch=False, burst=3)
    for _ in range(3):
        reader.update([(1, _CROP)])
    assert counting.calls == 3


def test_reads_back_off_after_the_burst_is_exhausted() -> None:
    counting = _CyclingReader()
    reader = _vehicle_reader(counting, watch=False, burst=2, interval=3)
    for _ in range(2):
        reader.update([(1, _CROP)])
    assert counting.calls == 2
    for _ in range(4):
        reader.update([(1, _CROP)])
    assert counting.calls == 3


def test_confirmed_plate_stops_being_reread() -> None:
    counting = _ConstantReader("AB123")
    reader = _vehicle_reader(counting, watch=True)
    for _ in range(2):
        reader.update([(1, _CROP)])
    reads_at_confirmation = counting.calls
    reader.update([(1, _CROP)])
    assert counting.calls == reads_at_confirmation


def test_absent_vehicle_track_is_forgotten() -> None:
    reader = _vehicle_reader(_ConstantReader("AB123"), watch=True)
    for _ in range(2):
        reader.update([(1, _CROP)])
    assert reader.update([]) == {}


def test_unwatched_plate_is_only_seen() -> None:
    reader = _vehicle_reader(_ConstantReader("ZZ999"), watch=False)
    for _ in range(2):
        reader.update([(1, _CROP)])
    confirmed = reader.update([(1, _CROP)])
    assert confirmed[1].decision is PlateDecision.SEEN
