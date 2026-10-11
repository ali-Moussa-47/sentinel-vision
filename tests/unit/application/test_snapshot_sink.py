from __future__ import annotations

from pathlib import Path

import numpy as np

from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.application.snapshot_sink import SnapshotSink
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult


class SpyWriter:
    def __init__(self) -> None:
        self.saved: tuple[str, float] | None = None

    def save(
        self, frame: np.ndarray, observation: FaceObservation, subject_label: str, score: float
    ) -> Path:
        self.saved = (subject_label, score)
        return Path("snapshot.jpg")


def test_snapshot_sink_forwards_label_and_score_to_writer() -> None:
    writer = SpyWriter()
    face = RecognizedFace(
        FaceObservation(0, 0, 10, 10, 0.9), RecognitionResult.potential_match("moussa", 0.93)
    )
    SnapshotSink(writer).on_match(np.zeros((2, 2, 3), dtype=np.uint8), face, "moussa")
    assert writer.saved == ("moussa", 0.93)
