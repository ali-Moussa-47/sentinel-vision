from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from sentinel_vision.plate.domain.plate_number import PlateNumber


class PlateDecision(Enum):
    WATCHED = auto()
    SEEN = auto()
    LOW_CONFIDENCE = auto()


@dataclass(frozen=True)
class PlateRecognitionResult:
    decision: PlateDecision
    plate: PlateNumber | None
    confidence: float

    @classmethod
    def watched(cls, plate: PlateNumber, confidence: float) -> PlateRecognitionResult:
        return cls(PlateDecision.WATCHED, plate, confidence)

    @classmethod
    def seen(cls, plate: PlateNumber, confidence: float) -> PlateRecognitionResult:
        return cls(PlateDecision.SEEN, plate, confidence)

    @classmethod
    def low_confidence(cls, confidence: float) -> PlateRecognitionResult:
        return cls(PlateDecision.LOW_CONFIDENCE, None, confidence)
