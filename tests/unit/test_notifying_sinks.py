from __future__ import annotations

import numpy as np

from sentinel_vision.bootstrap.notifying_sinks import NotifyingMatchSink, NotifyingPlateSink
from sentinel_vision.communication.domain.alert import Alert
from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult

_FRAME = np.zeros((40, 40, 3), dtype=np.uint8)


class _CapturingNotifier:
    def __init__(self) -> None:
        self.alerts: list[Alert] = []

    def notify(self, alert: Alert) -> None:
        self.alerts.append(alert)


def test_match_sink_builds_alert_with_subject_and_image() -> None:
    notifier = _CapturingNotifier()
    face = RecognizedFace(FaceObservation(0, 0, 20, 20, 0.9), RecognitionResult.potential_match("alice", 0.8))
    NotifyingMatchSink(notifier, "garden").on_match(_FRAME, face, "alice")
    [alert] = notifier.alerts
    assert "alice" in alert.body
    assert alert.image is not None


def test_plate_sink_builds_alert_with_plate_and_image() -> None:
    notifier = _CapturingNotifier()
    result = PlateRecognitionResult.watched(PlateNumber.normalize("AB123"), 0.95)
    NotifyingPlateSink(notifier, "garden").on_watched(_FRAME, (0, 0, 20, 20), result)
    [alert] = notifier.alerts
    assert "AB123" in alert.body
    assert alert.image is not None
