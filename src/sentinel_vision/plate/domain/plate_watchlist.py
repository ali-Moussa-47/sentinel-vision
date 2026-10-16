from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sentinel_vision.plate.domain.plate_number import PlateNumber


@dataclass(frozen=True)
class PlateWatchlist:
    plates: frozenset[PlateNumber]

    @classmethod
    def of(cls, raw_plates: Iterable[str]) -> PlateWatchlist:
        return cls(frozenset(PlateNumber.normalize(raw) for raw in raw_plates))

    def contains(self, plate: PlateNumber) -> bool:
        return plate in self.plates

    @property
    def size(self) -> int:
        return len(self.plates)
