from __future__ import annotations

from datetime import datetime

import numpy as np

from sentinel_vision.communication.application.email_sender import EmailSender
from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace


class EmailAlertSink:
    def __init__(self, sender: EmailSender, recipient: EmailAddress, camera_name: str) -> None:
        self._sender = sender
        self._recipient = recipient
        self._camera = camera_name

    def on_match(self, frame: np.ndarray, face: RecognizedFace, subject_label: str) -> None:
        moment = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"Sentinel Vision: potential match {subject_label}"
        body = (
            f"Potential match: {subject_label}\n"
            f"Similarity: {face.result.score:.2f}\n"
            f"Camera: {self._camera}\n"
            f"Time: {moment}\n"
        )
        self._sender.send(EmailMessage(self._recipient, subject, body))
