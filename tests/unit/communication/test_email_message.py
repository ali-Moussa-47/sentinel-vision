from __future__ import annotations

import pytest

from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_message import (
    EmailMessage,
    EmailMessageInvalidError,
)

_RECIPIENT = EmailAddress("alerts@example.com")


def test_valid_message_is_accepted() -> None:
    message = EmailMessage(_RECIPIENT, "Match", "Body")
    assert message.subject == "Match"


def test_blank_subject_is_rejected() -> None:
    with pytest.raises(EmailMessageInvalidError):
        EmailMessage(_RECIPIENT, "   ", "Body")


def test_blank_body_is_rejected() -> None:
    with pytest.raises(EmailMessageInvalidError):
        EmailMessage(_RECIPIENT, "Match", "   ")
