from __future__ import annotations

import pytest

from sentinel_vision.config import AppConfig


def test_default_config_is_valid() -> None:
    AppConfig()


def test_confirmation_window_smaller_than_confirm_frames_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(confirm_frames=5, confirmation_window=3)


def test_threshold_out_of_cosine_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(recognition_threshold=1.5)


def test_min_detection_score_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(min_detection_score=1.5)


def test_negative_reconnect_attempts_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(reconnect_attempts=-1)


def test_non_positive_face_minimum_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(min_face_pixels=0)


@pytest.mark.parametrize("threshold", [-0.01, 1.01])
def test_track_iou_threshold_out_of_range_is_rejected(threshold: float) -> None:
    with pytest.raises(ValueError):
        AppConfig(track_iou_threshold=threshold)


def test_negative_track_max_misses_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(track_max_misses=-1)


def test_non_positive_detector_size_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(det_size=(0, 320))


def test_detection_threshold_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(det_threshold=1.01)


def test_negative_capture_cooldown_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(capture_cooldown_seconds=-1.0)


@pytest.mark.parametrize("smoothing", [-0.01, 1.0])
def test_box_smoothing_out_of_range_is_rejected(smoothing: float) -> None:
    with pytest.raises(ValueError):
        AppConfig(box_smoothing=smoothing)


def test_detection_score_threshold_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(detection_score_threshold=1.5)


def test_plates_without_detection_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppConfig(plates_enabled=True, detection_enabled=False)
