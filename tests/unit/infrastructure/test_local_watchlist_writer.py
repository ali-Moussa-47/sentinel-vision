from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from sentinel_vision.recognition.infrastructure.watchlist.local_watchlist_writer import (
    LocalWatchlistWriter,
)

_IMAGE = np.zeros((8, 8, 3), dtype=np.uint8)


def test_save_creates_reference_under_subject_directory(tmp_path: Path) -> None:
    path = LocalWatchlistWriter(tmp_path).save("Moussa", _IMAGE)
    assert path == tmp_path / "moussa" / "ref_1.png"
    assert path.exists()


def test_label_is_normalised_into_subject_directory(tmp_path: Path) -> None:
    path = LocalWatchlistWriter(tmp_path).save("  Awa Diop  ", _IMAGE)
    assert path.parent.name == "awa_diop"


def test_successive_saves_do_not_overwrite(tmp_path: Path) -> None:
    writer = LocalWatchlistWriter(tmp_path)
    first = writer.save("moussa", _IMAGE)
    second = writer.save("moussa", _IMAGE)
    assert first.name == "ref_1.png"
    assert second.name == "ref_2.png"


def test_path_traversal_label_stays_within_root(tmp_path: Path) -> None:
    path = LocalWatchlistWriter(tmp_path).save("../../escaped", _IMAGE)
    assert path.resolve().is_relative_to(tmp_path.resolve())


def test_label_without_usable_characters_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        LocalWatchlistWriter(tmp_path).save("...", _IMAGE)


def test_numbering_gap_does_not_overwrite_existing_reference(tmp_path: Path) -> None:
    subject_dir = tmp_path / "moussa"
    subject_dir.mkdir()
    (subject_dir / "ref_1.png").write_bytes(b"")
    (subject_dir / "ref_3.png").write_bytes(b"")
    path = LocalWatchlistWriter(tmp_path).save("moussa", _IMAGE)
    assert path.name == "ref_4.png"
