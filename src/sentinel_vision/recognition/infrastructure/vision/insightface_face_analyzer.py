from __future__ import annotations

import numpy as np
from insightface.app import FaceAnalysis

from sentinel_vision.config import AppConfig
from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace, FaceAnalysisError
from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_observation import FaceObservation


class FaceAnalyzerInitializationError(RuntimeError):
    pass


class InsightFaceFaceAnalyzer:
    def __init__(self, config: AppConfig) -> None:
        try:
            self._app = FaceAnalysis(
                name=config.model_name,
                allowed_modules=["detection", "recognition"],
                providers=list(config.providers),
            )
            self._app.prepare(
                ctx_id=0,
                det_thresh=config.det_threshold,
                det_size=config.det_size,
            )
        except Exception as exc:
            raise FaceAnalyzerInitializationError(str(exc)) from exc

    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]:
        try:
            faces = self._app.get(frame)
        except Exception as exc:
            raise FaceAnalysisError(str(exc)) from exc

        height, width = frame.shape[:2]
        analyzed: list[AnalyzedFace] = []
        for face in faces:
            try:
                observation = FaceObservation.from_bbox(
                    tuple(face.bbox), float(face.det_score), width, height
                )
            except ValueError:
                continue
            try:
                embedding = FaceEmbedding(tuple(face.normed_embedding.tolist()))
            except ValueError as exc:
                raise FaceAnalysisError(f"model produced an invalid embedding: {exc}") from exc
            analyzed.append(AnalyzedFace(observation, embedding))
        return analyzed
