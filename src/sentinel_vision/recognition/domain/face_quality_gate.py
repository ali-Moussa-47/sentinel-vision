from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.recognition.domain.face_observation import FaceObservation


@dataclass(frozen=True)
class FaceQualityGate:
    min_face_pixels: int
    min_detection_score: float

    def is_reliable(self, observation: FaceObservation) -> bool:
        return (
            min(observation.width, observation.height) >= self.min_face_pixels
            and observation.detection_score >= self.min_detection_score
        )
