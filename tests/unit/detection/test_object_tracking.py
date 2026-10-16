from __future__ import annotations

from sentinel_vision.detection.application.object_tracking import ObjectTracker
from sentinel_vision.detection.domain.detected_object import DetectedObject


def _person(x1: int = 0, y1: int = 0, x2: int = 100, y2: int = 100) -> DetectedObject:
    return DetectedObject("person", x1, y1, x2, y2, 0.9)


def _tracker() -> ObjectTracker:
    return ObjectTracker(iou_threshold=0.3, max_misses=2)


def test_new_detection_gets_a_track_id() -> None:
    [tracked] = _tracker().update([_person()])
    assert tracked.track_id == 1
    assert tracked.observation.label == "person"


def test_overlapping_detection_keeps_the_same_id() -> None:
    tracker = _tracker()
    first = tracker.update([_person()])[0]
    moved = tracker.update([_person(10, 0, 110, 100)])[0]
    assert moved.track_id == first.track_id


def test_two_distinct_objects_get_distinct_ids() -> None:
    tracked = _tracker().update([_person(), _person(200, 200, 300, 300)])
    assert {t.track_id for t in tracked} == {1, 2}


def test_different_label_at_same_place_is_not_associated() -> None:
    tracker = _tracker()
    person = tracker.update([_person()])[0]
    car = tracker.update([DetectedObject("car", 0, 0, 100, 100, 0.9)])[0]
    assert car.track_id != person.track_id


def test_disappeared_object_gets_a_new_id_when_it_returns() -> None:
    tracker = _tracker()
    first = tracker.update([_person()])[0]
    for _ in range(3):
        tracker.update([])
    returned = tracker.update([_person()])[0]
    assert returned.track_id != first.track_id


def test_reset_restarts_id_allocation() -> None:
    tracker = _tracker()
    tracker.update([_person()])
    tracker.reset()
    assert tracker.update([_person()])[0].track_id == 1
