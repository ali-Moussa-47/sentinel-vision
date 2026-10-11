from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.communication.domain.email_address import EmailAddress


class EmailMessageInvalidError(ValueError):
    pass


@dataclass(frozen=True)
class EmailMessage:
    recipient: EmailAddress
    subject: str
    body: str

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise EmailMessageInvalidError("subject must not be blank")
        if not self.body.strip():
            raise EmailMessageInvalidError("body must not be blank")
