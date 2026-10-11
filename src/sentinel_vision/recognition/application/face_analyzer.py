from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_observation import FaceObservation


class FaceAnalysisError(RuntimeError):
    pass


@dataclass(frozen=True)
class AnalyzedFace:
    observation: FaceObservation
    embedding: FaceEmbedding


class FaceAnalyzer(Protocol):
    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]: ...
