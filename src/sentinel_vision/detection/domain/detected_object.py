from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedObject:
    label: str
    x1: int
    y1: int
    x2: int
    y2: int
    score: float

    def __post_init__(self) -> None:
        if not self.label:
            raise ValueError("label must not be empty")
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError(f"degenerate box: {(self.x1, self.y1, self.x2, self.y2)}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be within [0, 1]")

    def iou(self, other: DetectedObject) -> float:
        inter_width = max(0, min(self.x2, other.x2) - max(self.x1, other.x1))
        inter_height = max(0, min(self.y2, other.y2) - max(self.y1, other.y1))
        intersection = inter_width * inter_height
        if intersection == 0:
            return 0.0
        self_area = (self.x2 - self.x1) * (self.y2 - self.y1)
        other_area = (other.x2 - other.x1) * (other.y2 - other.y1)
        return intersection / (self_area + other_area - intersection)
