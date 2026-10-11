from __future__ import annotations

import pytest

from sentinel_vision.recognition.domain.recognition_policy import RecognitionPolicy
from sentinel_vision.recognition.domain.recognition_result import Decision
from sentinel_vision.recognition.domain.watchlist import Candidate

_POLICY = RecognitionPolicy(match_threshold=0.45)


def test_no_candidate_is_unknown() -> None:
    assert _POLICY.decide(None).decision is Decision.UNKNOWN


def test_candidate_below_threshold_is_unknown_with_its_score() -> None:
    result = _POLICY.decide(Candidate("Moussa", 0.44))
    assert result.decision is Decision.UNKNOWN
    assert result.score == pytest.approx(0.44)


def test_candidate_exactly_at_threshold_is_potential_match() -> None:
    assert _POLICY.decide(Candidate("Moussa", 0.45)).decision is Decision.POTENTIAL_MATCH


def test_candidate_above_threshold_is_potential_match_with_label() -> None:
    result = _POLICY.decide(Candidate("Moussa", 0.9))
    assert result.decision is Decision.POTENTIAL_MATCH
    assert result.subject_label == "Moussa"
