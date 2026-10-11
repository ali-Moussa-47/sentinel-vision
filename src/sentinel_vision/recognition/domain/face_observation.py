from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FaceObservation:
    x1: int
    y1: int
    x2: int
    y2: int
    detection_score: float

    @classmethod
    def from_bbox(
        cls,
        bbox: tuple[float, float, float, float],
        detection_score: float,
        frame_width: int,
        frame_height: int,
    ) -> FaceObservation:
        raw_x1, raw_y1, raw_x2, raw_y2 = (round(value) for value in bbox)
        x1 = min(max(raw_x1, 0), frame_width)
        x2 = min(max(raw_x2, 0), frame_width)
        y1 = min(max(raw_y1, 0), frame_height)
        y2 = min(max(raw_y2, 0), frame_height)
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"degenerate bbox after clamping: {(x1, y1, x2, y2)}")
        return cls(x1, y1, x2, y2, float(detection_score))

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    def iou(self, other: FaceObservation) -> float:
        inter_width = max(0, min(self.x2, other.x2) - max(self.x1, other.x1))
        inter_height = max(0, min(self.y2, other.y2) - max(self.y1, other.y1))
        intersection = inter_width * inter_height
        if intersection == 0:
            return 0.0
        union = self.width * self.height + other.width * other.height - intersection
        return intersection / union
