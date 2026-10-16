from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

import numpy as np

from sentinel_vision.plate.domain.plate_recognition_result import (
    PlateDecision,
    PlateRecognitionResult,
)

_Box = tuple[int, int, int, int]


class PlateSink(Protocol):
    def on_watched(self, frame: np.ndarray, box: _Box, result: PlateRecognitionResult) -> None: ...


class PlateAlerter:
    def __init__(
        self,
        sinks: list[PlateSink],
        cooldown_seconds: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._sinks = sinks
        self._cooldown_seconds = cooldown_seconds
        self._now = now
        self._last_alert: dict[str, float] = {}

    def process(self, frame: np.ndarray, entries: list[tuple[_Box, PlateRecognitionResult]]) -> None:
        moment = self._now()
        for box, result in entries:
            if result.decision is not PlateDecision.WATCHED or result.plate is None:
                continue
            key = result.plate.value
            previous = self._last_alert.get(key)
            if previous is not None and moment - previous < self._cooldown_seconds:
                continue
            for sink in self._sinks:
                sink.on_watched(frame, box, result)
            self._last_alert[key] = moment
