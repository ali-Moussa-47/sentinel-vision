from __future__ import annotations

import pytest

from sentinel_vision.detection.domain.detected_object import DetectedObject


def test_valid_object_is_constructed() -> None:
    obj = DetectedObject("person", 10, 20, 110, 220, 0.8)
    assert obj.label == "person"


def test_empty_label_is_rejected() -> None:
    with pytest.raises(ValueError):
        DetectedObject("", 10, 20, 110, 220, 0.8)


def test_degenerate_box_is_rejected() -> None:
    with pytest.raises(ValueError):
        DetectedObject("car", 50, 20, 50, 220, 0.8)


def test_score_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        DetectedObject("car", 10, 20, 110, 220, 1.5)


def test_iou_of_identical_boxes_is_one() -> None:
    box = DetectedObject("person", 0, 0, 100, 100, 0.9)
    assert box.iou(box) == pytest.approx(1.0)


def test_iou_of_disjoint_boxes_is_zero() -> None:
    a = DetectedObject("person", 0, 0, 10, 10, 0.9)
    b = DetectedObject("person", 50, 50, 60, 60, 0.9)
    assert a.iou(b) == 0.0


def test_iou_of_half_overlapping_boxes() -> None:
    a = DetectedObject("person", 0, 0, 100, 100, 0.9)
    b = DetectedObject("person", 50, 0, 150, 100, 0.9)
    assert a.iou(b) == pytest.approx(1 / 3)
