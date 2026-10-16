from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.domain.tracked_object import TrackedObject


@dataclass
class _Track:
    track_id: int
    observation: DetectedObject
    misses: int = 0


class ObjectTracker:
    def __init__(self, iou_threshold: float, max_misses: int) -> None:
        self._iou_threshold = iou_threshold
        self._max_misses = max_misses
        self._tracks: list[_Track] = []
        self._next_id = 0

    def reset(self) -> None:
        self._tracks = []
        self._next_id = 0

    def update(self, detections: list[DetectedObject]) -> list[TrackedObject]:
        matched: set[int] = set()
        tracked: list[TrackedObject] = []
        for detection in detections:
            track = self._associate(detection, matched)
            if track is None:
                self._next_id += 1
                track = _Track(self._next_id, detection)
                self._tracks.append(track)
            matched.add(id(track))
            track.observation = detection
            track.misses = 0
            tracked.append(TrackedObject(track.track_id, detection))
        self._drop_stale(matched)
        return tracked

    def _associate(self, detection: DetectedObject, matched: set[int]) -> _Track | None:
        best: _Track | None = None
        best_iou = self._iou_threshold
        for track in self._tracks:
            if id(track) in matched or track.observation.label != detection.label:
                continue
            overlap = detection.iou(track.observation)
            if overlap >= best_iou:
                best = track
                best_iou = overlap
        return best

    def _drop_stale(self, matched: set[int]) -> None:
        survivors: list[_Track] = []
        for track in self._tracks:
            if id(track) in matched:
                survivors.append(track)
                continue
            track.misses += 1
            if track.misses <= self._max_misses:
                survivors.append(track)
        self._tracks = survivors
