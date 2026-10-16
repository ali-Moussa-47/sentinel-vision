from __future__ import annotations

import pytest

from sentinel_vision.communication.domain.alert import Alert, AlertImage


def test_valid_alert_is_constructed() -> None:
    alert = Alert("Title", "Body")
    assert alert.image is None


def test_blank_title_is_rejected() -> None:
    with pytest.raises(ValueError):
        Alert("  ", "Body")


def test_blank_body_is_rejected() -> None:
    with pytest.raises(ValueError):
        Alert("Title", "  ")


def test_image_validates_content_type_and_content() -> None:
    with pytest.raises(ValueError):
        AlertImage("x.jpg", "imagejpeg", b"xx")
    with pytest.raises(ValueError):
        AlertImage("x.jpg", "image/jpeg", b"")
