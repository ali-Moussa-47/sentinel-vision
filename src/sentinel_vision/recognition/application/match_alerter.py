from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

import numpy as np

from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.recognition_result import Decision


class MatchSink(Protocol):
    def on_match(self, frame: np.ndarray, face: RecognizedFace, subject_label: str) -> None: ...


class MatchAlerter:
    def __init__(
        self,
        sinks: list[MatchSink],
        cooldown_seconds: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._sinks = sinks
        self._cooldown_seconds = cooldown_seconds
        self._now = now
        self._last_alert: dict[str, float] = {}

    def process(self, frame: np.ndarray, faces: list[RecognizedFace]) -> None:
        moment = self._now()
        for face in faces:
            if face.result.decision is not Decision.POTENTIAL_MATCH:
                continue
            label = face.result.subject_label
            if label is None:
                continue
            previous = self._last_alert.get(label)
            if previous is not None and moment - previous < self._cooldown_seconds:
                continue
            for sink in self._sinks:
                sink.on_match(frame, face, label)
            self._last_alert[label] = moment
