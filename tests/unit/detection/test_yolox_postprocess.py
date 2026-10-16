from __future__ import annotations

import numpy as np
import pytest

from sentinel_vision.detection.infrastructure.yolox_postprocess import decode, make_grid, nms


def test_grid_covers_all_anchors_with_strides() -> None:
    grid, stride = make_grid(416, 416)
    assert grid.shape[0] == 52 * 52 + 26 * 26 + 13 * 13
    assert tuple(grid[0]) == (0, 0)
    assert stride[0] == 8
    assert stride[-1] == 32


def test_decode_applies_grid_stride_and_combines_scores() -> None:
    predictions = np.zeros((21, 85), dtype=np.float32)
    predictions[0, 4] = 0.9
    predictions[0, 5 + 3] = 0.8
    boxes, scores, class_ids = decode(predictions, 32, 32)
    assert tuple(boxes[0]) == (-4.0, -4.0, 4.0, 4.0)
    assert class_ids[0] == 3
    assert scores[0] == pytest.approx(0.72, abs=1e-5)


def test_nms_keeps_best_and_drops_overlaps() -> None:
    boxes = np.array([[0, 0, 10, 10], [1, 1, 11, 11], [100, 100, 110, 110]], dtype=np.float32)
    scores = np.array([0.9, 0.8, 0.7], dtype=np.float32)
    assert nms(boxes, scores, iou_threshold=0.5) == [0, 2]
