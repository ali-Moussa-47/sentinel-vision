from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class FaceEmbedding:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("face embedding must not be empty")
        if not all(math.isfinite(value) for value in self.values):
            raise ValueError("face embedding must contain only finite values")

    def similarity_to(self, other: FaceEmbedding) -> float:
        if len(self.values) != len(other.values):
            raise ValueError("cannot compare embeddings of different dimensions")
        dot = sum(a * b for a, b in zip(self.values, other.values))
        norm = _norm(self.values) * _norm(other.values)
        if norm == 0:
            raise ValueError("cannot compute similarity for a zero-norm embedding")
        return dot / norm


def _norm(values: tuple[float, ...]) -> float:
    return math.sqrt(sum(value * value for value in values))
