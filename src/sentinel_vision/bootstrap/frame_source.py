from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import replace
from types import TracebackType
from typing import Protocol, Self

import cv2
import numpy as np

from sentinel_vision.config import AppConfig

_CAMERA_URL_ENV = "SENTINEL_CAMERA_URL"


class CameraError(RuntimeError):
    pass


def resolve_camera_config(config: AppConfig, camera: int | None, source: str | None) -> AppConfig:
    url = source or os.environ.get(_CAMERA_URL_ENV)
    if url:
        return replace(config, camera_url=url)
    if camera is not None:
        return replace(config, camera_index=camera)
    return config


def mask_credentials(source: str) -> str:
    if "://" in source and "@" in source:
        scheme, rest = source.split("://", 1)
        return f"{scheme}://***@{rest.split('@', 1)[1]}"
    return source


class FrameSource(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def read(self) -> np.ndarray: ...


class WebcamSource:
    def __init__(self, index: int, width: int, height: int) -> None:
        self._index = index
        self._width = width
        self._height = height
        self._capture: cv2.VideoCapture | None = None

    def __enter__(self) -> Self:
        capture = _opened(cv2.VideoCapture(self._index, cv2.CAP_DSHOW), f"camera {self._index}")
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._capture = capture
        return self

    def read(self) -> np.ndarray:
        return _read(self._capture, f"camera {self._index}")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        _release(self._capture)
        self._capture = None


class StreamSource:
    def __init__(self, url: str, timeout_ms: int) -> None:
        self._url = url
        self._timeout_ms = timeout_ms
        self._capture: cv2.VideoCapture | None = None

    def __enter__(self) -> Self:
        params = [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
            self._timeout_ms,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC,
            self._timeout_ms,
        ]
        capture = cv2.VideoCapture(self._url, cv2.CAP_FFMPEG, params)
        capture = _opened(capture, f"stream {mask_credentials(self._url)}")
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._capture = capture
        return self

    def read(self) -> np.ndarray:
        return _read(self._capture, f"stream {mask_credentials(self._url)}")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        _release(self._capture)
        self._capture = None


class ResilientFrameSource:
    def __init__(
        self,
        create_source: Callable[[], FrameSource],
        reconnect_attempts: int,
        reconnect_backoff: float,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._create_source = create_source
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_backoff = reconnect_backoff
        self._sleep = sleep
        self._source: FrameSource | None = None
        self._reconnect_count = 0

    @property
    def reconnect_count(self) -> int:
        return self._reconnect_count

    def __enter__(self) -> Self:
        self._source = self._create_source().__enter__()
        return self

    def read(self) -> np.ndarray:
        if self._source is None:
            raise CameraError("frame source is not open")
        try:
            return self._source.read()
        except CameraError:
            return self._reconnect_and_read()

    def _reconnect_and_read(self) -> np.ndarray:
        last_error = "unknown error"
        for _ in range(self._reconnect_attempts):
            self._sleep(self._reconnect_backoff)
            self._close()
            try:
                self._source = self._create_source().__enter__()
                frame = self._source.read()
                self._reconnect_count += 1
                return frame
            except CameraError as error:
                last_error = str(error)
        raise CameraError(
            f"stream lost after {self._reconnect_attempts} reconnect attempts: {last_error}"
        )

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._close()

    def _close(self) -> None:
        if self._source is not None:
            self._source.__exit__(None, None, None)
            self._source = None


def create_frame_source(config: AppConfig) -> FrameSource:
    if config.camera_url is not None:
        return StreamSource(config.camera_url, config.stream_timeout_ms)
    return WebcamSource(config.camera_index, config.frame_width, config.frame_height)


def open_frame_source(config: AppConfig) -> ResilientFrameSource:
    return ResilientFrameSource(
        lambda: create_frame_source(config),
        config.reconnect_attempts,
        config.reconnect_backoff,
    )


def _opened(capture: cv2.VideoCapture, label: str) -> cv2.VideoCapture:
    if not capture.isOpened():
        capture.release()
        raise CameraError(f"could not open {label}")
    return capture


def _read(capture: cv2.VideoCapture | None, label: str) -> np.ndarray:
    if capture is None:
        raise CameraError(f"{label} is not open")
    ok, frame = capture.read()
    if not ok or frame is None:
        raise CameraError(f"failed to read frame from {label}")
    return frame


def _release(capture: cv2.VideoCapture | None) -> None:
    if capture is not None:
        capture.release()
