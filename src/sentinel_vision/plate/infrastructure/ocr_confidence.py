from __future__ import annotations

from collections.abc import Sequence


def aggregate_confidence(per_character: Sequence[float] | float | None) -> float:
    if per_character is None:
        return 0.0
    if isinstance(per_character, (int, float)):
        value = float(per_character)
    else:
        scores = [float(score) for score in per_character]
        value = min(scores) if scores else 0.0
    return min(max(value, 0.0), 1.0)
