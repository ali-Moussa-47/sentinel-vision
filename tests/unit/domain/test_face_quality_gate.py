from __future__ import annotations

from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate

_GATE = FaceQualityGate(min_face_pixels=112, min_detection_score=0.65)


def _observation(side: int = 120, score: float = 0.9) -> FaceObservation:
    return FaceObservation(0, 0, side, side, score)


def test_face_smaller_than_minimum_is_not_reliable() -> None:
    assert _GATE.is_reliable(_observation(side=111)) is False


def test_face_short_on_one_side_is_not_reliable() -> None:
    assert _GATE.is_reliable(FaceObservation(0, 0, 200, 100, 0.9)) is False


def test_face_with_low_detection_score_is_not_reliable() -> None:
    assert _GATE.is_reliable(_observation(score=0.64)) is False


def test_large_and_confident_face_is_reliable() -> None:
    assert _GATE.is_reliable(_observation(side=120, score=0.9)) is True


def test_face_exactly_at_minimum_size_and_score_is_reliable() -> None:
    assert _GATE.is_reliable(_observation(side=112, score=0.65)) is True
