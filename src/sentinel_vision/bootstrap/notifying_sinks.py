from __future__ import annotations

from datetime import datetime

import numpy as np

from sentinel_vision.bootstrap.image_jpeg import encode_jpeg
from sentinel_vision.communication.application.alert_notifier import AlertNotifier
from sentinel_vision.communication.domain.alert import Alert, AlertImage
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult
from sentinel_vision.recognition.application.recognize_frame import RecognizedFace

_Box = tuple[int, int, int, int]


class NotifyingMatchSink:
    def __init__(self, notifier: AlertNotifier, camera_name: str) -> None:
        self._notifier = notifier
        self._camera = camera_name

    def on_match(self, frame: np.ndarray, face: RecognizedFace, subject_label: str) -> None:
        box = (face.observation.x1, face.observation.y1, face.observation.x2, face.observation.y2)
        body = (
            f"{subject_label}\n"
            f"Similarity: {face.result.score:.2f}\n"
            f"Camera: {self._camera}\n"
            f"Time: {_now()}"
        )
        self._notifier.notify(Alert("Sentinel Vision: potential match", body, _image(frame, box, subject_label)))


class NotifyingPlateSink:
    def __init__(self, notifier: AlertNotifier, camera_name: str) -> None:
        self._notifier = notifier
        self._camera = camera_name

    def on_watched(self, frame: np.ndarray, box: _Box, result: PlateRecognitionResult) -> None:
        if result.plate is None:
            return
        plate = result.plate.value
        body = (
            f"{plate}\n"
            f"Confidence: {result.confidence:.2f}\n"
            f"Camera: {self._camera}\n"
            f"Time: {_now()}"
        )
        self._notifier.notify(Alert("Sentinel Vision: watched plate", body, _image(frame, box, plate)))


def _image(frame: np.ndarray, box: _Box, name: str) -> AlertImage | None:
    content = encode_jpeg(frame, box)
    if content is None:
        return None
    return AlertImage(f"{name}.jpg", "image/jpeg", content)


def _now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
