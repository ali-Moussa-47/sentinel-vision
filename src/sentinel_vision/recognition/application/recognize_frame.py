from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sentinel_vision.recognition.application.face_analyzer import (
    AnalyzedFace,
    FaceAnalysisError,
    FaceAnalyzer,
)
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.domain.recognition_policy import RecognitionPolicy
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult
from sentinel_vision.recognition.domain.watchlist import Watchlist


@dataclass(frozen=True)
class RecognizedFace:
    observation: FaceObservation
    result: RecognitionResult


@dataclass(frozen=True)
class FrameRecognition:
    faces: tuple[RecognizedFace, ...]
    recognition_available: bool

    @classmethod
    def recognized(cls, faces: tuple[RecognizedFace, ...]) -> FrameRecognition:
        return cls(faces, True)

    @classmethod
    def unavailable(cls) -> FrameRecognition:
        return cls((), False)


class RecognizeFrame:
    def __init__(
        self,
        analyzer: FaceAnalyzer,
        watchlist: Watchlist,
        quality_gate: FaceQualityGate,
        policy: RecognitionPolicy,
    ) -> None:
        self._analyzer = analyzer
        self._watchlist = watchlist
        self._quality_gate = quality_gate
        self._policy = policy

    def __call__(self, frame: np.ndarray) -> FrameRecognition:
        try:
            analyzed = self._analyzer.analyze(frame)
        except FaceAnalysisError:
            return FrameRecognition.unavailable()
        return FrameRecognition.recognized(
            tuple(
                RecognizedFace(face.observation, self._recognize(face))
                for face in analyzed
            )
        )

    def _recognize(self, face: AnalyzedFace) -> RecognitionResult:
        if not self._quality_gate.is_reliable(face.observation):
            return RecognitionResult.insufficient_quality()
        return self._policy.decide(self._watchlist.best_match(face.embedding))
