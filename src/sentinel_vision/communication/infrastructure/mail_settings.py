from __future__ import annotations

import os
from dataclasses import dataclass

from sentinel_vision.communication.domain.email_address import (
    EmailAddress,
    EmailAddressInvalidError,
)


class MailSettingsError(RuntimeError):
    pass


@dataclass(frozen=True)
class MailSettings:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipient: EmailAddress
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> MailSettings:
        host = os.environ.get("SENTINEL_SMTP_HOST")
        sender = os.environ.get("SENTINEL_SMTP_FROM")
        recipient = os.environ.get("SENTINEL_SMTP_TO")
        if not host or not sender or not recipient:
            raise MailSettingsError(
                "set SENTINEL_SMTP_HOST, SENTINEL_SMTP_FROM and SENTINEL_SMTP_TO"
            )
        try:
            return cls(
                host=host,
                port=int(os.environ.get("SENTINEL_SMTP_PORT", "587")),
                username=os.environ.get("SENTINEL_SMTP_USER", ""),
                password=os.environ.get("SENTINEL_SMTP_PASSWORD", ""),
                sender=sender,
                recipient=EmailAddress(recipient),
                use_tls=os.environ.get("SENTINEL_SMTP_TLS", "1") not in ("0", "false", "False"),
            )
        except (ValueError, EmailAddressInvalidError) as error:
            raise MailSettingsError(f"invalid mail configuration: {error}") from error
