from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from sentinel_vision.plate.domain.plate_reading import PlateReading


class PlateReadingError(RuntimeError):
    pass


@dataclass(frozen=True)
class AnalyzedPlate:
    x1: int
    y1: int
    x2: int
    y2: int
    reading: PlateReading


class PlateReader(Protocol):
    def read(self, frame: np.ndarray) -> list[AnalyzedPlate]: ...
