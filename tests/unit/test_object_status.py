from __future__ import annotations

from sentinel_vision.bootstrap.main import _object_status

_DETECTOR = object()


def test_disabled_detection_has_no_status() -> None:
    assert _object_status(False, None, True, 0) is None


def test_running_detection_reports_the_count() -> None:
    assert _object_status(True, _DETECTOR, True, 2) == "DETECT 2"


def test_enabled_but_failed_to_initialize_is_unavailable() -> None:
    assert _object_status(True, None, True, 0) == "DETECT UNAVAILABLE"


def test_mid_stream_detection_error_is_unavailable() -> None:
    assert _object_status(True, _DETECTOR, False, 0) == "DETECT UNAVAILABLE"
