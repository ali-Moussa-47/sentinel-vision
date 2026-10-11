from __future__ import annotations

from sentinel_vision.communication.application.email_sender import EmailSendingError
from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.communication.infrastructure.background_email_sender import (
    BackgroundEmailSender,
)

_MESSAGE = EmailMessage(EmailAddress("to@example.com"), "Match", "Body")


class RecordingSender:
    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


class FailingSender:
    def send(self, message: EmailMessage) -> None:
        raise EmailSendingError("smtp down")


def test_messages_are_delivered_to_the_delegate() -> None:
    delegate = RecordingSender()
    sender = BackgroundEmailSender(delegate)
    sender.send(_MESSAGE)
    sender.close()
    assert delegate.sent == [_MESSAGE]


def test_delivery_failure_is_reported_not_raised() -> None:
    errors: list[EmailSendingError] = []
    sender = BackgroundEmailSender(FailingSender(), on_error=errors.append)
    sender.send(_MESSAGE)
    sender.close()
    assert len(errors) == 1
