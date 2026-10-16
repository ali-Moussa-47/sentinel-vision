from __future__ import annotations

from pathlib import Path

import numpy as np

from sentinel_vision.plate.infrastructure.capture.local_plate_snapshot_writer import (
    LocalPlateSnapshotWriter,
)

_FRAME = np.zeros((40, 40, 3), dtype=np.uint8)


def test_snapshot_is_written_under_a_per_plate_directory(tmp_path: Path) -> None:
    writer = LocalPlateSnapshotWriter(tmp_path, "garden-cam")
    path = writer.save(_FRAME, (5, 5, 30, 30), "AB123")
    assert path.exists()
    assert path.parent.name == "AB123"
    assert path.suffix == ".jpg"
    assert "garden-cam" in path.name
