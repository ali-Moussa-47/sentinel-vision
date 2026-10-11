from __future__ import annotations

import numpy as np

from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace, FaceAnalysisError
from sentinel_vision.recognition.application.recognize_frame import RecognizeFrame
from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.domain.recognition_policy import RecognitionPolicy
from sentinel_vision.recognition.domain.recognition_result import Decision
from sentinel_vision.recognition.domain.watchlist import Watchlist, WatchlistSubject

_KNOWN = FaceEmbedding((1.0, 0.0))
_IMPOSTOR = FaceEmbedding((0.0, 1.0))
_FRAME = np.zeros((2, 2, 3), dtype=np.uint8)
_GATE = FaceQualityGate(min_face_pixels=112, min_detection_score=0.65)
_POLICY = RecognitionPolicy(match_threshold=0.45)


def _reliable(embedding: FaceEmbedding) -> AnalyzedFace:
    return AnalyzedFace(FaceObservation(0, 0, 120, 120, 0.9), embedding)


def _too_far(embedding: FaceEmbedding) -> AnalyzedFace:
    return AnalyzedFace(FaceObservation(0, 0, 80, 80, 0.9), embedding)


class StubAnalyzer:
    def __init__(self, *faces: AnalyzedFace) -> None:
        self._faces = list(faces)

    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]:
        return self._faces


class FailingAnalyzer:
    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]:
        raise FaceAnalysisError("inference failed")


def _recognize(analyzer: object) -> RecognizeFrame:
    watchlist = Watchlist((WatchlistSubject("moussa", "Moussa", (_KNOWN,)),))
    return RecognizeFrame(analyzer, watchlist, _GATE, _POLICY)


def test_no_detected_face_yields_no_faces() -> None:
    assert _recognize(StubAnalyzer())(_FRAME).faces == ()


def test_known_reliable_face_is_potential_match() -> None:
    [recognized] = _recognize(StubAnalyzer(_reliable(_KNOWN)))(_FRAME).faces
    assert recognized.result.decision is Decision.POTENTIAL_MATCH


def test_impostor_reliable_face_is_unknown() -> None:
    [recognized] = _recognize(StubAnalyzer(_reliable(_IMPOSTOR)))(_FRAME).faces
    assert recognized.result.decision is Decision.UNKNOWN


def test_too_far_face_is_insufficient_quality_even_when_embedding_matches() -> None:
    [recognized] = _recognize(StubAnalyzer(_too_far(_KNOWN)))(_FRAME).faces
    assert recognized.result.decision is Decision.INSUFFICIENT_QUALITY


def test_every_detected_face_produces_one_result() -> None:
    faces = _recognize(StubAnalyzer(_reliable(_KNOWN), _reliable(_IMPOSTOR)))(_FRAME).faces
    assert len(faces) == 2


def test_successful_recognition_is_marked_available() -> None:
    assert _recognize(StubAnalyzer(_reliable(_KNOWN)))(_FRAME).recognition_available is True


def test_analysis_failure_is_reported_as_unavailable_not_unknown() -> None:
    outcome = _recognize(FailingAnalyzer())(_FRAME)
    assert outcome.recognition_available is False
    assert outcome.faces == ()
