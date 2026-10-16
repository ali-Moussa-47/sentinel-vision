from __future__ import annotations

import cv2
import numpy as np

from sentinel_vision.plate.infrastructure.image_crop import crop_box

_Box = tuple[int, int, int, int]


def encode_jpeg(frame: np.ndarray, box: _Box) -> bytes | None:
    encoded, buffer = cv2.imencode(".jpg", crop_box(frame, box))
    if not encoded:
        return None
    return buffer.tobytes()
