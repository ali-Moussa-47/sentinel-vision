from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.infrastructure.capture.local_snapshot_writer import (
    LocalSnapshotWriter,
)

_FRAME = np.full((200, 200, 3), 128, dtype=np.uint8)
_OBSERVATION = FaceObservation(50, 50, 150, 150, 0.9)


def test_snapshot_is_written_under_sanitised_subject_directory(tmp_path: Path) -> None:
    path = LocalSnapshotWriter(tmp_path, "garden").save(_FRAME, _OBSERVATION, "Moussa Demo", 0.91)
    assert path.exists()
    assert path.parent == tmp_path / "moussa_demo"
    assert "garden" in path.name


def test_snapshot_is_a_readable_image(tmp_path: Path) -> None:
    path = LocalSnapshotWriter(tmp_path, "garden").save(_FRAME, _OBSERVATION, "moussa", 0.9)
    assert cv2.imread(str(path)) is not None


def test_malicious_subject_label_stays_within_root(tmp_path: Path) -> None:
    path = LocalSnapshotWriter(tmp_path, "garden").save(_FRAME, _OBSERVATION, "../escape", 0.9)
    assert path.resolve().is_relative_to(tmp_path.resolve())


def test_empty_subject_label_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        LocalSnapshotWriter(tmp_path, "garden").save(_FRAME, _OBSERVATION, "...", 0.9)
