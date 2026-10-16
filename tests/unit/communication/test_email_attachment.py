from __future__ import annotations

import pytest

from sentinel_vision.communication.domain.email_attachment import EmailAttachment


def test_valid_attachment_splits_content_type() -> None:
    attachment = EmailAttachment("plate.jpg", "image/jpeg", b"xxx")
    assert (attachment.maintype, attachment.subtype) == ("image", "jpeg")


def test_blank_filename_is_rejected() -> None:
    with pytest.raises(ValueError):
        EmailAttachment("  ", "image/jpeg", b"xxx")


def test_malformed_content_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        EmailAttachment("plate.jpg", "imagejpeg", b"xxx")


def test_empty_content_is_rejected() -> None:
    with pytest.raises(ValueError):
        EmailAttachment("plate.jpg", "image/jpeg", b"")
