from __future__ import annotations

import cv2
import numpy as np

from sentinel_vision.recognition.application.recognize_frame import FrameRecognition, RecognizedFace
from sentinel_vision.recognition.domain.recognition_result import Decision, RecognitionResult

_MATCH = (80, 83, 239)
_UNKNOWN = (194, 183, 174)
_QUALITY = (246, 181, 100)
_TEXT = (250, 247, 245)
_TEXT_MUTED = (141, 129, 119)
_PANEL = (16, 20, 17)
_READY = (106, 187, 102)
_WARNING = (77, 183, 255)

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_SCALE = 0.5
_STATUS_BAR_H = 36


def render(
    frame: np.ndarray,
    outcome: FrameRecognition,
    fps: float,
    watchlist_size: int,
    camera_label: str,
    provider_label: str,
) -> None:
    subjects = f"{watchlist_size} SUBJECT" + ("S" if watchlist_size != 1 else "")
    tail = f"{subjects}    {fps:4.1f} FPS    CAM {camera_label}    {provider_label}"

    if not outcome.recognition_available:
        _draw_status_bar(frame, _WARNING, "RECOGNITION UNAVAILABLE", tail)
        return

    for face in outcome.faces:
        _draw_face(frame, face)
    faces_label = f"{len(outcome.faces)} FACE" + ("S" if len(outcome.faces) != 1 else "")
    _draw_status_bar(frame, _READY, "SYSTEM READY", f"{faces_label}    {tail}")


def _draw_face(frame: np.ndarray, face: RecognizedFace) -> None:
    box = face.observation
    color, label = _appearance(face.result)
    cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), color, 2)
    _draw_label(frame, label, box.x1, box.y1)


def _appearance(result: RecognitionResult) -> tuple[tuple[int, int, int], str]:
    if result.decision is Decision.POTENTIAL_MATCH:
        return _MATCH, f"POTENTIAL MATCH   {result.subject_label}   {result.score:.2f}"
    if result.decision is Decision.INSUFFICIENT_QUALITY:
        return _QUALITY, "MOVE CLOSER"
    return _UNKNOWN, "UNKNOWN"


def _draw_label(frame: np.ndarray, text: str, x: int, box_top: int) -> None:
    (text_width, text_height), baseline = cv2.getTextSize(text, _FONT, _SCALE, 1)
    pad = 6
    height = text_height + baseline + pad
    top = box_top - height if box_top - height >= 0 else box_top
    cv2.rectangle(frame, (x, top), (x + text_width + pad * 2, top + height), _PANEL, -1)
    cv2.putText(
        frame, text, (x + pad, top + text_height + pad // 2), _FONT, _SCALE, _TEXT, 1, cv2.LINE_AA
    )


def _draw_status_bar(
    frame: np.ndarray, dot_color: tuple[int, int, int], status: str, diagnostics: str
) -> None:
    height, width = frame.shape[:2]
    mid = height - _STATUS_BAR_H // 2
    cv2.rectangle(frame, (0, height - _STATUS_BAR_H), (width, height), _PANEL, -1)

    cv2.circle(frame, (18, mid), 5, dot_color, -1)
    cv2.putText(frame, status, (34, mid + 5), _FONT, _SCALE, _TEXT, 1, cv2.LINE_AA)

    (text_width, _), _ = cv2.getTextSize(diagnostics, _FONT, _SCALE, 1)
    cv2.putText(
        frame, diagnostics, (width - text_width - 16, mid + 5), _FONT, _SCALE, _TEXT_MUTED, 1,
        cv2.LINE_AA,
    )
