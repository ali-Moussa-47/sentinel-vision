from __future__ import annotations

from typing import Protocol

from sentinel_vision.communication.domain.email_message import EmailMessage


class EmailSendingError(RuntimeError):
    pass


class EmailSender(Protocol):
    def send(self, message: EmailMessage) -> None: ...
