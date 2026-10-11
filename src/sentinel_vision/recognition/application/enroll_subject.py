from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate


class EnrollmentError(RuntimeError):
    pass


class ReferenceWriter(Protocol):
    def save(self, label: str, frame: np.ndarray) -> Path: ...


class EnrollSubject:
    def __init__(self, writer: ReferenceWriter, quality_gate: FaceQualityGate) -> None:
        self._writer = writer
        self._quality_gate = quality_gate

    def enroll(self, label: str, frame: np.ndarray, faces: list[AnalyzedFace]) -> Path:
        if not label.strip():
            raise EnrollmentError("subject label must not be empty")
        if not faces:
            raise EnrollmentError("no face detected; position one face in view")
        if len(faces) > 1:
            raise EnrollmentError(f"{len(faces)} faces detected; capture only one subject")
        if not self._quality_gate.is_reliable(faces[0].observation):
            raise EnrollmentError("face too small or detection too weak; move closer")
        return self._writer.save(label, frame)
