from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.plate.domain.plate_number import PlateNumber


@dataclass(frozen=True)
class PlateReading:
    plate: PlateNumber
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
