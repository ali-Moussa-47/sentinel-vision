from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from sentinel_vision.recognition.application.recognize_frame import RecognizedFace
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.match_confirmation import MatchConfirmation
from sentinel_vision.recognition.domain.recognition_result import RecognitionResult


@dataclass
class _Track:
    observation: FaceObservation
    history: deque[RecognitionResult]
    misses: int = 0


class FaceTracker:
    def __init__(
        self,
        confirmation: MatchConfirmation,
        window_frames: int,
        iou_threshold: float,
        max_misses: int,
    ) -> None:
        self._confirmation = confirmation
        self._window_frames = window_frames
        self._iou_threshold = iou_threshold
        self._max_misses = max_misses
        self._tracks: list[_Track] = []

    def reset(self) -> None:
        self._tracks = []

    def update(self, faces: list[RecognizedFace]) -> list[RecognizedFace]:
        matched: set[int] = set()
        stabilized: list[RecognizedFace] = []
        for face in faces:
            track = self._associate(face.observation, matched)
            if track is None:
                track = _Track(face.observation, deque(maxlen=self._window_frames))
                self._tracks.append(track)
            matched.add(id(track))
            track.observation = face.observation
            track.misses = 0
            track.history.append(face.result)
            stabilized.append(
                RecognizedFace(face.observation, self._confirmation.confirm(track.history))
            )
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
