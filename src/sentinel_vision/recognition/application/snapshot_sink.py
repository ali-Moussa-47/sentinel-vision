from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation


class SnapshotWriter(Protocol):
    def save(
        self, frame: np.ndarray, observation: FaceObservation, subject_label: str, score: float
    ) -> Path: ...


class SnapshotSink:
    def __init__(self, writer: SnapshotWriter) -> None:
        self._writer = writer

    def on_match(self, frame: np.ndarray, face: RecognizedFace, subject_label: str) -> None:
        self._writer.save(frame, face.observation, subject_label, face.result.score)
