from __future__ import annotations

from enum import Enum

import cv2
import numpy as np

_WIDTH = 960
_HEIGHT = 540

_BACKGROUND = (16, 13, 11)
_ERROR = (80, 83, 239)
_TEXT = (250, 247, 245)
_TEXT_MUTED = (141, 129, 119)

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_MARGIN = 64
_HINT = "Press R to retry      Q to quit"

_RETRY_KEYS = {ord("r"), ord("R")}
_QUIT_KEYS = {ord("q"), 27}
_POLL_MS = 50


class UserAction(Enum):
    RETRY = "RETRY"
    QUIT = "QUIT"


def render_status(title: str, detail: str) -> np.ndarray:
    canvas = np.full((_HEIGHT, _WIDTH, 3), _BACKGROUND, dtype=np.uint8)
    cv2.putText(canvas, title, (_MARGIN, 232), _FONT, 1.0, _ERROR, 2, cv2.LINE_AA)
    cv2.putText(canvas, _fit(detail), (_MARGIN, 288), _FONT, 0.6, _TEXT, 1, cv2.LINE_AA)
    cv2.putText(canvas, _HINT, (_MARGIN, _HEIGHT - _MARGIN), _FONT, 0.5, _TEXT_MUTED, 1, cv2.LINE_AA)
    return canvas


def _fit(detail: str) -> str:
    limit = 92
    return detail if len(detail) <= limit else detail[: limit - 1] + "…"


class StatusScreen:
    def __init__(self, window_title: str) -> None:
        self._window = window_title

    def ask(self, title: str, detail: str) -> UserAction:
        canvas = render_status(title, detail)
        cv2.namedWindow(self._window, cv2.WINDOW_NORMAL)
        while True:
            cv2.imshow(self._window, canvas)
            key = cv2.waitKey(_POLL_MS) & 0xFF
            if key in _RETRY_KEYS:
                return UserAction.RETRY
            if key in _QUIT_KEYS:
                return UserAction.QUIT
            if cv2.getWindowProperty(self._window, cv2.WND_PROP_VISIBLE) < 1:
                return UserAction.QUIT
