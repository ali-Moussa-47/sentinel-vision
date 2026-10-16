from __future__ import annotations

from datetime import datetime

import numpy as np

from sentinel_vision.bootstrap.image_jpeg import encode_jpeg
from sentinel_vision.communication.application.email_sender import EmailSender
from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_attachment import EmailAttachment
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult

_Box = tuple[int, int, int, int]


class PlateEmailAlertSink:
    def __init__(self, sender: EmailSender, recipient: EmailAddress, camera_name: str) -> None:
        self._sender = sender
        self._recipient = recipient
        self._camera = camera_name

    def on_watched(self, frame: np.ndarray, box: _Box, result: PlateRecognitionResult) -> None:
        if result.plate is None:
            return
        moment = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        plate = result.plate.value
        subject = f"Sentinel Vision: watched plate {plate}"
        body = (
            f"Watched plate: {plate}\n"
            f"Confidence: {result.confidence:.2f}\n"
            f"Camera: {self._camera}\n"
            f"Time: {moment}\n"
        )
        attachments = _attachment(frame, box, plate)
        self._sender.send(EmailMessage(self._recipient, subject, body, attachments))


def _attachment(frame: np.ndarray, box: _Box, plate: str) -> tuple[EmailAttachment, ...]:
    content = encode_jpeg(frame, box)
    if content is None:
        return ()
    return (EmailAttachment(f"plate_{plate}.jpg", "image/jpeg", content),)
