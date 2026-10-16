from __future__ import annotations

import pytest

from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.domain.tracked_object import TrackedObject

_OBJECT = DetectedObject("person", 0, 0, 100, 100, 0.9)


def test_valid_tracked_object_is_constructed() -> None:
    tracked = TrackedObject(1, _OBJECT)
    assert tracked.track_id == 1
    assert tracked.observation is _OBJECT


def test_non_positive_track_id_is_rejected() -> None:
    with pytest.raises(ValueError):
        TrackedObject(0, _OBJECT)
