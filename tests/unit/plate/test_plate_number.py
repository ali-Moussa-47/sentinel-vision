from __future__ import annotations

import pytest

from sentinel_vision.plate.domain.plate_number import PlateNumber


def test_normalize_uppercases_and_strips_separators() -> None:
    assert PlateNumber.normalize("ab-123 cd").value == "AB123CD"


def test_normalized_plates_compare_equal() -> None:
    assert PlateNumber.normalize("ab 123") == PlateNumber.normalize("AB-123")


def test_empty_after_cleaning_is_rejected() -> None:
    with pytest.raises(ValueError):
        PlateNumber.normalize("  --  ")


def test_direct_non_alphanumeric_value_is_rejected() -> None:
    with pytest.raises(ValueError):
        PlateNumber("AB 123")
