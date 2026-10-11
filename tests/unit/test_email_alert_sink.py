from __future__ import annotations

import numpy as np

from sentinel_vision.bootstrap.email_alert_sink import EmailAlertSink
from sentinel_vision.communication.domain.email_address import EmailAddress
from sentinel_vision.communication.domain.email_message import EmailMessage
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult


class RecordingSender:
    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


def test_email_alert_builds_message_with_match_details() -> None:
    sender = RecordingSender()
    sink = EmailAlertSink(sender, EmailAddress("to@example.com"), "garden")
    face = RecognizedFace(
        FaceObservation(0, 0, 10, 10, 0.9), RecognitionResult.potential_match("Moussa", 0.93)
    )
    sink.on_match(np.zeros((2, 2, 3), dtype=np.uint8), face, "Moussa")
    [message] = sender.sent
    assert message.recipient.value == "to@example.com"
    assert "Moussa" in message.subject
    assert "0.93" in message.body
    assert "garden" in message.body
