from __future__ import annotations

from pathlib import Path

from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_watchlist import PlateWatchlist


def load_plate_watchlist(path: Path) -> PlateWatchlist:
    if not path.exists():
        return PlateWatchlist(frozenset())
    plates: set[PlateNumber] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        try:
            plates.add(PlateNumber.normalize(entry))
        except ValueError:
            continue
    return PlateWatchlist(frozenset(plates))
