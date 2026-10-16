from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.match_confirmation import MatchConfirmation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult

_Box = tuple[int, int, int, int]


@dataclass
class _Track:
    observation: FaceObservation
    display_box: _Box
    history: deque[RecognitionResult]
    misses: int = 0


class FaceTracker:
    def __init__(
        self,
        confirmation: MatchConfirmation,
        window_frames: int,
        iou_threshold: float,
        max_misses: int,
        box_smoothing: float = 0.0,
    ) -> None:
        self._confirmation = confirmation
        self._window_frames = window_frames
        self._iou_threshold = iou_threshold
        self._max_misses = max_misses
        self._box_smoothing = box_smoothing
        self._tracks: list[_Track] = []

    def reset(self) -> None:
        self._tracks = []

    def update(self, faces: list[RecognizedFace]) -> list[RecognizedFace]:
        matched: set[int] = set()
        stabilized: list[RecognizedFace] = []
        for face in faces:
            track = self._associate(face.observation, matched)
            if track is None:
                track = _Track(face.observation, _box(face.observation), deque(maxlen=self._window_frames))
                self._tracks.append(track)
            matched.add(id(track))
            track.observation = face.observation
            track.display_box = _lerp_box(track.display_box, _box(face.observation), self._box_smoothing)
            track.misses = 0
            track.history.append(face.result)
            display = _displayed(track.display_box, face.observation)
            stabilized.append(RecognizedFace(display, self._confirmation.confirm(track.history)))
        self._drop_stale(matched)
        return stabilized

    def _associate(self, observation: FaceObservation, matched: set[int]) -> _Track | None:
        best: _Track | None = None
        best_iou = self._iou_threshold
        for track in self._tracks:
            if id(track) in matched:
                continue
            overlap = observation.iou(track.observation)
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


def _box(observation: FaceObservation) -> _Box:
    return (observation.x1, observation.y1, observation.x2, observation.y2)


def _lerp(previous: int, current: int, smoothing: float) -> int:
    return round(smoothing * previous + (1.0 - smoothing) * current)


def _lerp_box(previous: _Box, current: _Box, smoothing: float) -> _Box:
    return (
        _lerp(previous[0], current[0], smoothing),
        _lerp(previous[1], current[1], smoothing),
        _lerp(previous[2], current[2], smoothing),
        _lerp(previous[3], current[3], smoothing),
    )


def _displayed(box: _Box, source: FaceObservation) -> FaceObservation:
    return FaceObservation(box[0], box[1], box[2], box[3], source.detection_score)
