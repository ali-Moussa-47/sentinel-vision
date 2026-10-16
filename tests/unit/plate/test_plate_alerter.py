from __future__ import annotations

import numpy as np

from sentinel_vision.plate.application.plate_alerter import PlateAlerter
from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult

_FRAME = np.zeros((20, 20, 3), dtype=np.uint8)
_BOX = (0, 0, 10, 10)


class _RecordingSink:
    def __init__(self) -> None:
        self.plates: list[str] = []

    def on_watched(self, frame: np.ndarray, box: tuple[int, int, int, int], result: PlateRecognitionResult) -> None:
        assert result.plate is not None
        self.plates.append(result.plate.value)


def _watched(value: str) -> PlateRecognitionResult:
    return PlateRecognitionResult.watched(PlateNumber.normalize(value), 0.9)


def _seen(value: str) -> PlateRecognitionResult:
    return PlateRecognitionResult.seen(PlateNumber.normalize(value), 0.9)


def test_watched_plate_triggers_the_sink() -> None:
    sink = _RecordingSink()
    alerter = PlateAlerter([sink], cooldown_seconds=30.0, now=lambda: 0.0)
    alerter.process(_FRAME, [(_BOX, _watched("AB123"))])
    assert sink.plates == ["AB123"]


def test_seen_plate_does_not_trigger_the_sink() -> None:
    sink = _RecordingSink()
    alerter = PlateAlerter([sink], cooldown_seconds=30.0, now=lambda: 0.0)
    alerter.process(_FRAME, [(_BOX, _seen("AB123"))])
    assert sink.plates == []


def test_same_plate_is_debounced_within_cooldown() -> None:
    sink = _RecordingSink()
    clock = [0.0]
    alerter = PlateAlerter([sink], cooldown_seconds=30.0, now=lambda: clock[0])
    alerter.process(_FRAME, [(_BOX, _watched("AB123"))])
    clock[0] = 10.0
    alerter.process(_FRAME, [(_BOX, _watched("AB123"))])
    assert sink.plates == ["AB123"]


def test_plate_alerts_again_after_cooldown() -> None:
    sink = _RecordingSink()
    clock = [0.0]
    alerter = PlateAlerter([sink], cooldown_seconds=30.0, now=lambda: clock[0])
    alerter.process(_FRAME, [(_BOX, _watched("AB123"))])
    clock[0] = 31.0
    alerter.process(_FRAME, [(_BOX, _watched("AB123"))])
    assert sink.plates == ["AB123", "AB123"]
