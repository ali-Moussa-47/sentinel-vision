from __future__ import annotations

import numpy as np

_Box = tuple[int, int, int, int]


def crop_box(frame: np.ndarray, box: _Box) -> np.ndarray:
    height, width = frame.shape[:2]
    x1 = max(0, box[0])
    y1 = max(0, box[1])
    x2 = min(width, box[2])
    y2 = min(height, box[3])
    return frame[y1:y2, x1:x2]
