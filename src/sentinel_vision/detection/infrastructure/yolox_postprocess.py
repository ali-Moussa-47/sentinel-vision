from __future__ import annotations

import numpy as np

_STRIDES = (8, 16, 32)


def make_grid(input_height: int, input_width: int) -> tuple[np.ndarray, np.ndarray]:
    grids: list[np.ndarray] = []
    strides: list[np.ndarray] = []
    for stride in _STRIDES:
        rows, cols = input_height // stride, input_width // stride
        xv, yv = np.meshgrid(np.arange(cols), np.arange(rows))
        grid = np.stack((xv, yv), axis=2).reshape(-1, 2)
        grids.append(grid)
        strides.append(np.full((grid.shape[0], 1), stride))
    return np.concatenate(grids, axis=0), np.concatenate(strides, axis=0)


def decode(predictions: np.ndarray, input_height: int, input_width: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    grid, stride = make_grid(input_height, input_width)
    centers = (predictions[:, 0:2] + grid) * stride
    sizes = np.exp(predictions[:, 2:4]) * stride
    objectness = predictions[:, 4]
    class_logits = predictions[:, 5:]
    class_ids = class_logits.argmax(axis=1)
    confidence = objectness * class_logits.max(axis=1)
    half = sizes / 2.0
    boxes = np.concatenate((centers - half, centers + half), axis=1)
    return boxes, confidence, class_ids


def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size > 0:
        best = int(order[0])
        keep.append(best)
        rest = order[1:]
        if rest.size == 0:
            break
        overlaps = _iou(boxes[best], boxes[rest])
        order = rest[overlaps < iou_threshold]
    return keep


def _iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])
    inter = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    area = (box[2] - box[0]) * (box[3] - box[1])
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union = area + areas - inter
    return np.where(union > 0.0, inter / union, 0.0)
