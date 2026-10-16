from __future__ import annotations

import pytest

from sentinel_vision.plate.infrastructure.ocr_confidence import aggregate_confidence


def test_per_character_list_uses_the_weakest_character() -> None:
    assert aggregate_confidence([0.99, 0.80, 0.95]) == pytest.approx(0.80)


def test_scalar_confidence_is_passed_through() -> None:
    assert aggregate_confidence(0.73) == pytest.approx(0.73)


def test_missing_confidence_is_zero() -> None:
    assert aggregate_confidence(None) == 0.0
    assert aggregate_confidence([]) == 0.0


def test_out_of_range_values_are_clamped() -> None:
    assert aggregate_confidence([1.5]) == 1.0
    assert aggregate_confidence([-0.2]) == 0.0
