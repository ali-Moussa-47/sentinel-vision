from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from sentinel_vision.recognition.application.enroll_subject import EnrollmentError, EnrollSubject
from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace
from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate

_FRAME = np.zeros((2, 2, 3), dtype=np.uint8)
_GATE = FaceQualityGate(min_face_pixels=112, min_detection_score=0.65)
_RELIABLE = AnalyzedFace(FaceObservation(0, 0, 120, 120, 0.9), FaceEmbedding((1.0, 0.0)))
_TOO_FAR = AnalyzedFace(FaceObservation(0, 0, 80, 80, 0.9), FaceEmbedding((1.0, 0.0)))


class SpyWriter:
    def __init__(self) -> None:
        self.saved: tuple[str, np.ndarray] | None = None

    def save(self, label: str, frame: np.ndarray) -> Path:
        self.saved = (label, frame)
        return Path("data/watchlist/moussa/ref_1.png")


def _enroller(writer: object) -> EnrollSubject:
    return EnrollSubject(writer, _GATE)


def test_empty_label_is_rejected() -> None:
    with pytest.raises(EnrollmentError):
        _enroller(SpyWriter()).enroll("   ", _FRAME, [_RELIABLE])


def test_frame_without_face_is_rejected() -> None:
    with pytest.raises(EnrollmentError):
        _enroller(SpyWriter()).enroll("moussa", _FRAME, [])


def test_frame_with_multiple_faces_is_rejected() -> None:
    with pytest.raises(EnrollmentError):
        _enroller(SpyWriter()).enroll("moussa", _FRAME, [_RELIABLE, _RELIABLE])


def test_too_far_face_is_rejected() -> None:
    with pytest.raises(EnrollmentError):
        _enroller(SpyWriter()).enroll("moussa", _FRAME, [_TOO_FAR])


def test_single_reliable_face_is_written_as_reference() -> None:
    writer = SpyWriter()
    _enroller(writer).enroll("moussa", _FRAME, [_RELIABLE])
    assert writer.saved is not None
    assert writer.saved[0] == "moussa"
