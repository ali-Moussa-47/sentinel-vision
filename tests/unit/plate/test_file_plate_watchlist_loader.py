from __future__ import annotations

from pathlib import Path

from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.infrastructure.file_plate_watchlist_loader import load_plate_watchlist


def test_missing_file_yields_empty_watchlist(tmp_path: Path) -> None:
    assert load_plate_watchlist(tmp_path / "absent.txt").size == 0


def test_entries_are_normalized_comments_and_blanks_ignored(tmp_path: Path) -> None:
    path = tmp_path / "plates.txt"
    path.write_text("# wanted plates\nab-123-cd\n\n  ZZ 999  \n--\n", encoding="utf-8")
    watchlist = load_plate_watchlist(path)
    assert watchlist.size == 2
    assert watchlist.contains(PlateNumber.normalize("AB123CD"))
    assert watchlist.contains(PlateNumber("ZZ999"))
