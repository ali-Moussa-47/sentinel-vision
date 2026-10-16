from __future__ import annotations

from dataclasses import dataclass, field

from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_attachment import EmailAttachment


class EmailMessageInvalidError(ValueError):
    pass


@dataclass(frozen=True)
class EmailMessage:
    recipient: EmailAddress
    subject: str
    body: str
    attachments: tuple[EmailAttachment, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise EmailMessageInvalidError("subject must not be blank")
        if not self.body.strip():
            raise EmailMessageInvalidError("body must not be blank")
