from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace
from typing import Self

import numpy as np
import pytest

from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    ResilientFrameSource,
    StreamSource,
    WebcamSource,
    create_frame_source,
    mask_credentials,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.config import AppConfig

_FRAME = np.zeros((2, 2, 3), dtype=np.uint8)
_URL_CONFIG = replace(AppConfig(), camera_url="rtsp://192.168.1.50:554/stream1")


class _FakeSource:
    def __init__(self, reads: list[np.ndarray | CameraError], open_ok: bool = True) -> None:
        self._reads = reads
        self._open_ok = open_ok

    def __enter__(self) -> Self:
        if not self._open_ok:
            raise CameraError("cannot open")
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> np.ndarray:
        result = self._reads.pop(0)
        if isinstance(result, CameraError):
            raise result
        return result


def _resilient(sources: list[_FakeSource], attempts: int = 3) -> ResilientFrameSource:
    stream: Iterator[_FakeSource] = iter(sources)
    return ResilientFrameSource(
        lambda: next(stream), reconnect_attempts=attempts, reconnect_backoff=0.0, sleep=lambda _: None
    )


def test_local_config_creates_a_webcam_source() -> None:
    assert isinstance(create_frame_source(AppConfig()), WebcamSource)


def test_url_config_creates_a_stream_source() -> None:
    assert isinstance(create_frame_source(_URL_CONFIG), StreamSource)


def test_open_frame_source_is_resilient() -> None:
    assert isinstance(open_frame_source(AppConfig()), ResilientFrameSource)


def test_healthy_stream_returns_frames() -> None:
    with _resilient([_FakeSource([_FRAME])]) as camera:
        assert camera.read() is _FRAME


def test_transient_failure_reconnects_and_recovers() -> None:
    with _resilient([_FakeSource([CameraError("blip")]), _FakeSource([_FRAME])]) as camera:
        assert camera.read() is _FRAME


def test_reconnect_count_increments_on_recovery() -> None:
    with _resilient([_FakeSource([CameraError("blip")]), _FakeSource([_FRAME])]) as camera:
        camera.read()
        assert camera.reconnect_count == 1


def test_reconnect_count_is_zero_without_failures() -> None:
    with _resilient([_FakeSource([_FRAME])]) as camera:
        camera.read()
        assert camera.reconnect_count == 0


def test_persistent_failure_raises_after_attempts() -> None:
    sources = [_FakeSource([CameraError("down")]) for _ in range(5)]
    with _resilient(sources, attempts=2) as camera, pytest.raises(CameraError):
        camera.read()


def test_reconnect_recovers_even_when_reopen_fails_once() -> None:
    sources = [
        _FakeSource([CameraError("blip")]),
        _FakeSource([], open_ok=False),
        _FakeSource([_FRAME]),
    ]
    with _resilient(sources, attempts=3) as camera:
        assert camera.read() is _FRAME


def test_credentials_are_masked_in_stream_url() -> None:
    assert mask_credentials("rtsp://user:pass@10.0.0.5:554/s1") == "rtsp://***@10.0.0.5:554/s1"


def test_url_without_credentials_is_unchanged() -> None:
    url = "rtsp://10.0.0.5:554/s1"
    assert mask_credentials(url) == url


def test_source_argument_sets_stream_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SENTINEL_CAMERA_URL", raising=False)
    assert resolve_camera_config(AppConfig(), None, "rtsp://host/s").camera_url == "rtsp://host/s"


def test_camera_url_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTINEL_CAMERA_URL", "rtsp://env/s")
    assert resolve_camera_config(AppConfig(), None, None).camera_url == "rtsp://env/s"


def test_source_argument_overrides_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTINEL_CAMERA_URL", "rtsp://env/s")
    assert resolve_camera_config(AppConfig(), None, "rtsp://arg/s").camera_url == "rtsp://arg/s"


def test_camera_index_used_when_no_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SENTINEL_CAMERA_URL", raising=False)
    config = resolve_camera_config(AppConfig(), 2, None)
    assert config.camera_index == 2
    assert config.camera_url is None


def test_empty_environment_variable_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTINEL_CAMERA_URL", "")
    assert resolve_camera_config(AppConfig(), None, None).camera_url is None
