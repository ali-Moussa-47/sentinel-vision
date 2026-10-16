from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path


def is_expired(mtime: float, now: float, max_age_seconds: float) -> bool:
    return now - mtime > max_age_seconds


class CaptureRetention:
    def __init__(
        self, root: Path, max_age_seconds: float, now: Callable[[], float] = time.time
    ) -> None:
        self._root = root
        self._max_age_seconds = max_age_seconds
        self._now = now

    def purge(self) -> int:
        if not self._root.exists():
            return 0
        moment = self._now()
        removed = 0
        for path in self._root.rglob("*"):
            if path.is_file() and is_expired(path.stat().st_mtime, moment, self._max_age_seconds):
                path.unlink()
                removed += 1
        return removed
