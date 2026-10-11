from __future__ import annotations

from sentinel_vision.recognition.application.face_tracking import FaceTracker
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.match_confirmation import MatchConfirmation
from sentinel_vision.recognition.domain.recognition_result import Decision, RecognitionResult

_NEAR = FaceObservation(0, 0, 100, 100, 0.9)
_FAR = FaceObservation(400, 400, 500, 500, 0.9)
_UNKNOWN = RecognitionResult.unknown(0.2)


def _tracker() -> FaceTracker:
    return FaceTracker(MatchConfirmation(3), window_frames=5, iou_threshold=0.3, max_misses=2)


def _match() -> RecognitionResult:
    return RecognitionResult.potential_match("moussa", 0.9)


def _face(result: RecognitionResult, box: FaceObservation = _NEAR) -> RecognizedFace:
    return RecognizedFace(box, result)


def test_match_is_confirmed_only_after_enough_consistent_frames() -> None:
    tracker = _tracker()
    assert tracker.update([_face(_match())])[0].result.decision is not Decision.POTENTIAL_MATCH
    assert tracker.update([_face(_match())])[0].result.decision is not Decision.POTENTIAL_MATCH
    assert tracker.update([_face(_match())])[0].result.decision is Decision.POTENTIAL_MATCH


def test_single_frame_spike_is_not_confirmed() -> None:
    tracker = _tracker()
    tracker.update([_face(_UNKNOWN)])
    tracker.update([_face(_UNKNOWN)])
    assert tracker.update([_face(_match())])[0].result.decision is Decision.UNKNOWN


def test_faces_at_different_positions_are_tracked_independently() -> None:
    tracker = _tracker()
    stabilized = tracker.update([_face(_match(), _NEAR), _face(_match(), _FAR)])
    assert len(stabilized) == 2


def test_stale_track_is_dropped_and_must_reconfirm() -> None:
    tracker = _tracker()
    for _ in range(3):
        tracker.update([_face(_match())])
    for _ in range(3):
        tracker.update([])
    assert tracker.update([_face(_match())])[0].result.decision is not Decision.POTENTIAL_MATCH


def test_confirmed_identity_is_not_inherited_by_a_new_unknown_person() -> None:
    tracker = _tracker()
    for _ in range(3):
        tracker.update([_face(_match())])
    [result] = tracker.update([_face(_UNKNOWN)])
    assert result.result.decision is Decision.UNKNOWN


def test_reset_clears_confirmation_history() -> None:
    tracker = _tracker()
    for _ in range(3):
        tracker.update([_face(_match())])
    tracker.reset()
    assert tracker.update([_face(_match())])[0].result.decision is not Decision.POTENTIAL_MATCH
