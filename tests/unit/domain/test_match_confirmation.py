from __future__ import annotations

import pytest

from sentinel_vision.recognition.domain.match_confirmation import MatchConfirmation
from sentinel_vision.recognition.domain.recognition_result import Decision, RecognitionResult

_CONFIRM = MatchConfirmation(confirm_frames=3)
_UNKNOWN = RecognitionResult.unknown(0.2)
_INSUFFICIENT = RecognitionResult.insufficient_quality()


def _match(score: float = 0.9) -> RecognitionResult:
    return RecognitionResult.potential_match("moussa", score)


def test_empty_history_is_unknown() -> None:
    assert _CONFIRM.confirm([]).decision is Decision.UNKNOWN


def test_match_repeated_enough_is_confirmed() -> None:
    result = _CONFIRM.confirm([_match(), _match(), _match()])
    assert result.decision is Decision.POTENTIAL_MATCH
    assert result.subject_label == "moussa"


def test_single_match_spike_is_not_confirmed() -> None:
    result = _CONFIRM.confirm([_UNKNOWN, _match(), _UNKNOWN])
    assert result.decision is Decision.UNKNOWN


def test_confirmed_score_is_the_best_recent_match_score() -> None:
    result = _CONFIRM.confirm([_match(0.6), _match(0.8), _match(0.7)])
    assert result.score == pytest.approx(0.8)


def test_latest_insufficient_quality_is_reported_when_not_confirmed() -> None:
    assert _CONFIRM.confirm([_UNKNOWN, _INSUFFICIENT]).decision is Decision.INSUFFICIENT_QUALITY


def test_confirmed_match_is_dropped_when_latest_is_unknown() -> None:
    result = _CONFIRM.confirm([_match(), _match(), _match(), _UNKNOWN])
    assert result.decision is Decision.UNKNOWN


def test_new_subject_is_not_confirmed_from_previous_subject_history() -> None:
    alice = RecognitionResult.potential_match("alice", 0.9)
    bob = RecognitionResult.potential_match("bob", 0.9)
    result = _CONFIRM.confirm([alice, alice, alice, bob])
    assert result.decision is Decision.UNKNOWN
