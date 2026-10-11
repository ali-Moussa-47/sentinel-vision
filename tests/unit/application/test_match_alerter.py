from __future__ import annotations

import numpy as np

from sentinel_vision.recognition.application.match_alerter import MatchAlerter
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult

_FRAME = np.zeros((2, 2, 3), dtype=np.uint8)
_BOX = FaceObservation(0, 0, 10, 10, 0.9)


class SpySink:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def on_match(self, frame: np.ndarray, face: RecognizedFace, subject_label: str) -> None:
        self.calls.append(subject_label)


class _Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


def _match(label: str) -> RecognizedFace:
    return RecognizedFace(_BOX, RecognitionResult.potential_match(label, 0.9))


def _unknown() -> RecognizedFace:
    return RecognizedFace(_BOX, RecognitionResult.unknown(0.2))


def _alerter(sinks: list[SpySink], clock: _Clock, cooldown: float = 30.0) -> MatchAlerter:
    return MatchAlerter(sinks, cooldown, now=clock)


def test_only_matches_trigger_sinks() -> None:
    sink = SpySink()
    _alerter([sink], _Clock()).process(_FRAME, [_unknown()])
    assert sink.calls == []


def test_match_triggers_every_sink() -> None:
    first, second = SpySink(), SpySink()
    _alerter([first, second], _Clock()).process(_FRAME, [_match("moussa")])
    assert first.calls == ["moussa"]
    assert second.calls == ["moussa"]


def test_subject_is_not_realerted_within_cooldown() -> None:
    sink, clock = SpySink(), _Clock()
    alerter = _alerter([sink], clock)
    alerter.process(_FRAME, [_match("moussa")])
    clock.value = 10.0
    alerter.process(_FRAME, [_match("moussa")])
    assert sink.calls == ["moussa"]


def test_subject_is_realerted_after_cooldown() -> None:
    sink, clock = SpySink(), _Clock()
    alerter = _alerter([sink], clock)
    alerter.process(_FRAME, [_match("moussa")])
    clock.value = 31.0
    alerter.process(_FRAME, [_match("moussa")])
    assert sink.calls == ["moussa", "moussa"]


def test_different_subjects_each_trigger() -> None:
    sink = SpySink()
    _alerter([sink], _Clock()).process(_FRAME, [_match("awa"), _match("bob")])
    assert sink.calls == ["awa", "bob"]
