from __future__ import annotations

import smtplib
from email.message import EmailMessage as MimeEmailMessage

from sentinel_vision.communication.application.email_sender import EmailSendingError
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.communication.infrastructure.mail_settings import MailSettings


class SmtpEmailSender:
    def __init__(self, settings: MailSettings, timeout_seconds: float = 10.0) -> None:
        self._settings = settings
        self._timeout_seconds = timeout_seconds

    def send(self, message: EmailMessage) -> None:
        mime = build_mime(message, self._settings.sender)
        try:
            with smtplib.SMTP(
                self._settings.host, self._settings.port, timeout=self._timeout_seconds
            ) as smtp:
                if self._settings.use_tls:
                    smtp.starttls()
                if self._settings.username:
                    smtp.login(self._settings.username, self._settings.password)
                smtp.send_message(mime)
        except (OSError, smtplib.SMTPException) as error:
            raise EmailSendingError(
                f"failed to send email to {message.recipient.value}"
            ) from error


def build_mime(message: EmailMessage, sender: str) -> MimeEmailMessage:
    mime = MimeEmailMessage()
    mime["From"] = sender
    mime["To"] = message.recipient.value
    mime["Subject"] = message.subject
    mime.set_content(message.body)
    return mime
