from __future__ import annotations

from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_attachment import EmailAttachment
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.communication.infrastructure.smtp_email_sender import build_mime

_TO = EmailAddress("to@example.com")


def test_text_only_message_has_no_attachments() -> None:
    mime = build_mime(EmailMessage(_TO, "Subject", "Body"), "from@example.com")
    assert list(mime.iter_attachments()) == []


def test_message_with_image_attachment_is_included() -> None:
    attachment = EmailAttachment("plate.jpg", "image/jpeg", b"\xff\xd8\xff")
    mime = build_mime(EmailMessage(_TO, "Subject", "Body", (attachment,)), "from@example.com")
    attached = list(mime.iter_attachments())
    assert len(attached) == 1
    assert attached[0].get_filename() == "plate.jpg"
    assert attached[0].get_content_type() == "image/jpeg"
