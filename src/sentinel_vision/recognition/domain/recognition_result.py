from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    INSUFFICIENT_QUALITY = "INSUFFICIENT_QUALITY"
    UNKNOWN = "UNKNOWN"
    POTENTIAL_MATCH = "POTENTIAL_MATCH"


@dataclass(frozen=True)
class RecognitionResult:
    decision: Decision
    score: float
    subject_label: str | None = None

    @classmethod
    def insufficient_quality(cls) -> RecognitionResult:
        return cls(Decision.INSUFFICIENT_QUALITY, 0.0, None)

    @classmethod
    def unknown(cls, score: float) -> RecognitionResult:
        return cls(Decision.UNKNOWN, score, None)

    @classmethod
    def potential_match(cls, subject_label: str, score: float) -> RecognitionResult:
        return cls(Decision.POTENTIAL_MATCH, score, subject_label)
