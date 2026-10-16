from __future__ import annotations

from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_reading import PlateReading
from sentinel_vision.plate.domain.plate_reading_policy import PlateReadingPolicy
from sentinel_vision.plate.domain.plate_recognition_result import PlateDecision
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist

_POLICY = PlateReadingPolicy(min_confidence=0.6)
_WATCHLIST = PlateWatchlist.of(["AB-123-CD"])


def _reading(value: str, confidence: float) -> PlateReading:
    return PlateReading(PlateNumber.normalize(value), confidence)


def test_watched_plate_is_flagged() -> None:
    result = _POLICY.evaluate(_reading("ab123cd", 0.9), _WATCHLIST)
    assert result.decision is PlateDecision.WATCHED
    assert result.plate == PlateNumber("AB123CD")


def test_unknown_plate_is_only_seen() -> None:
    assert _POLICY.evaluate(_reading("zz999", 0.9), _WATCHLIST).decision is PlateDecision.SEEN


def test_low_confidence_reading_is_not_trusted() -> None:
    result = _POLICY.evaluate(_reading("ab123cd", 0.4), _WATCHLIST)
    assert result.decision is PlateDecision.LOW_CONFIDENCE
    assert result.plate is None


def test_watchlist_normalizes_its_entries() -> None:
    assert _WATCHLIST.contains(PlateNumber.normalize("AB 123 CD"))
