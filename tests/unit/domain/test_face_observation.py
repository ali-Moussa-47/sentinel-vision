from __future__ import annotations

import pytest

from sentinel_vision.recognition.domain.face_observation import FaceObservation


def test_from_bbox_rounds_coordinates_to_pixels() -> None:
    observation = FaceObservation.from_bbox((10.4, 20.6, 110.0, 220.0), 0.9, 640, 480)
    assert (observation.x1, observation.y1, observation.x2, observation.y2) == (10, 21, 110, 220)


def test_from_bbox_keeps_detection_score() -> None:
    observation = FaceObservation.from_bbox((10.0, 20.0, 110.0, 220.0), 0.93, 640, 480)
    assert observation.detection_score == pytest.approx(0.93)


def test_from_bbox_clamps_coordinates_to_frame_bounds() -> None:
    observation = FaceObservation.from_bbox((-5.0, -8.0, 700.0, 500.0), 0.5, 640, 480)
    assert (observation.x1, observation.y1, observation.x2, observation.y2) == (0, 0, 640, 480)


def test_from_bbox_rejects_box_with_no_area_after_clamping() -> None:
    with pytest.raises(ValueError):
        FaceObservation.from_bbox((-50.0, 10.0, -10.0, 100.0), 0.8, 640, 480)


def test_iou_of_identical_boxes_is_one() -> None:
    box = FaceObservation(0, 0, 100, 100, 0.9)
    assert box.iou(box) == pytest.approx(1.0)


def test_iou_of_disjoint_boxes_is_zero() -> None:
    assert FaceObservation(0, 0, 10, 10, 0.9).iou(FaceObservation(50, 50, 60, 60, 0.9)) == 0.0


def test_iou_of_half_overlapping_boxes() -> None:
    a = FaceObservation(0, 0, 100, 100, 0.9)
    b = FaceObservation(50, 0, 150, 100, 0.9)
    assert a.iou(b) == pytest.approx(1 / 3)
