from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.detection.domain.detected_object import DetectedObject


@dataclass(frozen=True)
class TrackedObject:
    track_id: int
    observation: DetectedObject

    def __post_init__(self) -> None:
        if self.track_id < 1:
            raise ValueError("track_id must be >= 1")
