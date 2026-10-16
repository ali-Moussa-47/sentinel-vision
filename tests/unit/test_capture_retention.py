from __future__ import annotations

import os
from pathlib import Path

from sentinel_vision.bootstrap.capture_retention import CaptureRetention, is_expired


def test_is_expired_compares_age_to_max() -> None:
    assert is_expired(mtime=0.0, now=100.0, max_age_seconds=60.0)
    assert not is_expired(mtime=50.0, now=100.0, max_age_seconds=60.0)


def test_purge_deletes_only_files_older_than_retention(tmp_path: Path) -> None:
    old = tmp_path / "plates" / "AB123" / "old.jpg"
    recent = tmp_path / "plates" / "AB123" / "recent.jpg"
    old.parent.mkdir(parents=True)
    old.write_bytes(b"x")
    recent.write_bytes(b"x")
    os.utime(old, (0, 0))
    os.utime(recent, (1_000_000, 1_000_000))

    retention = CaptureRetention(tmp_path, max_age_seconds=3600.0, now=lambda: 1_000_100.0)
    removed = retention.purge()

    assert removed == 1
    assert not old.exists()
    assert recent.exists()


def test_purge_on_missing_root_is_noop(tmp_path: Path) -> None:
    retention = CaptureRetention(tmp_path / "absent", max_age_seconds=1.0)
    assert retention.purge() == 0
