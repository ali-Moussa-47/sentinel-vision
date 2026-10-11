from __future__ import annotations

import re

_UNSAFE = re.compile(r"[^a-z0-9_-]+")


def safe_subject_id(label: str) -> str:
    cleaned = _UNSAFE.sub("", label.strip().lower().replace(" ", "_"))
    if not cleaned:
        raise ValueError(f"label has no usable characters for a subject id: {label!r}")
    return cleaned
