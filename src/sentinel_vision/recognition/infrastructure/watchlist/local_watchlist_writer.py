from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from sentinel_vision.recognition.infrastructure.paths import safe_subject_id


class LocalWatchlistWriter:
    def __init__(self, root: Path) -> None:
        self._root = root

    def save(self, label: str, frame: np.ndarray) -> Path:
        subject_dir = self._root / safe_subject_id(label)
        if not subject_dir.resolve().is_relative_to(self._root.resolve()):
            raise ValueError(f"subject directory escapes the watchlist root: {label!r}")
        subject_dir.mkdir(parents=True, exist_ok=True)
        path = subject_dir / f"ref_{_next_index(subject_dir)}.png"
        if not cv2.imwrite(str(path), frame):
            raise OSError(f"failed to write reference image: {path}")
        return path


def _next_index(subject_dir: Path) -> int:
    indices = [
        int(path.stem[4:])
        for path in subject_dir.glob("ref_*.png")
        if path.stem[4:].isdigit()
    ]
    return max(indices) + 1 if indices else 1
