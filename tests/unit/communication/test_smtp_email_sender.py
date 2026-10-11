from __future__ import annotations

from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.communication.infrastructure.smtp_email_sender import build_mime

_MESSAGE = EmailMessage(EmailAddress("to@example.com"), "Match: Moussa", "Score 0.93")


def test_mime_carries_sender_recipient_and_subject() -> None:
    mime = build_mime(_MESSAGE, "from@example.com")
    assert mime["From"] == "from@example.com"
    assert mime["To"] == "to@example.com"
    assert mime["Subject"] == "Match: Moussa"


def test_mime_body_matches_message() -> None:
    mime = build_mime(_MESSAGE, "from@example.com")
    assert mime.get_content().strip() == "Score 0.93"
