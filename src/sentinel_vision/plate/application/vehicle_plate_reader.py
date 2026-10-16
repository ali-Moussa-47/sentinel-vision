from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from sentinel_vision.plate.application.recognize_plate import RecognizedPlate, RecognizePlate
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult


@dataclass
class _VehicleState:
    plates: deque[str]
    confirmed: PlateRecognitionResult | None = None
    attempts: int = 0
    since_read: int = 0


@dataclass
class VehiclePlateReader:
    recognize: RecognizePlate
    burst_attempts: int
    read_interval: int
    confirm_count: int
    window: int
    _states: dict[int, _VehicleState] = field(default_factory=dict)

    def reset(self) -> None:
        self._states = {}

    def update(self, crops: list[tuple[int, np.ndarray]]) -> dict[int, PlateRecognitionResult]:
        active: set[int] = set()
        for track_id, crop in crops:
            active.add(track_id)
            state = self._states.setdefault(track_id, _VehicleState(deque(maxlen=self.window)))
            if self._should_read(state):
                state.attempts += 1
                state.since_read = 0
                self._read_into(state, crop)
            else:
                state.since_read += 1
        self._states = {track_id: state for track_id, state in self._states.items() if track_id in active}
        return {
            track_id: state.confirmed
            for track_id, state in self._states.items()
            if state.confirmed is not None
        }

    def _should_read(self, state: _VehicleState) -> bool:
        if state.confirmed is not None:
            return False
        if state.attempts < self.burst_attempts:
            return True
        return state.since_read >= self.read_interval

    def _read_into(self, state: _VehicleState, crop: np.ndarray) -> None:
        result = _best(self.recognize(crop))
        if result is None or result.plate is None:
            return
        state.plates.append(result.plate.value)
        if state.plates.count(result.plate.value) >= self.confirm_count:
            state.confirmed = result


def _best(plates: list[RecognizedPlate]) -> PlateRecognitionResult | None:
    readings = [plate.result for plate in plates if plate.result.plate is not None]
    if not readings:
        return None
    return max(readings, key=lambda result: result.confidence)
