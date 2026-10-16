from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from sentinel_vision.plate.infrastructure.image_crop import crop_box

_Box = tuple[int, int, int, int]


class PlateSnapshotWriteError(RuntimeError):
    pass


class LocalPlateSnapshotWriter:
    def __init__(self, root: Path, camera_name: str) -> None:
        self._root = root
        self._camera = _sanitize(camera_name) or "cam"

    def save(self, frame: np.ndarray, box: _Box, plate_value: str) -> Path:
        plate_dir = self._root / (_sanitize(plate_value) or "plate")
        plate_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S_%f")[:-3]
        path = plate_dir / f"{stamp}_{self._camera}.jpg"
        if not cv2.imwrite(str(path), crop_box(frame, box)):
            raise PlateSnapshotWriteError(f"failed to write plate snapshot: {path}")
        return path


def _sanitize(value: str) -> str:
    return "".join(character for character in value if character.isalnum() or character in "-_")
