from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import sentinel_vision

_SOURCES = tuple(Path(sentinel_vision.__file__).parent.rglob("*.py"))
_FIELD = re.compile(r"\{([^{}]*)\}")

_RAW_BIOMETRIC_TOKENS = ("embedding", ".values", "tolist")
_CREDENTIAL_TOKENS = ("self._url", "camera_url")


def _interpolated_fields() -> Iterator[tuple[str, str]]:
    for path in _SOURCES:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for field in _FIELD.findall(line):
                yield f"{path.name}:{number}", field


def test_source_files_are_found() -> None:
    assert _SOURCES


def test_no_raw_biometric_value_is_interpolated() -> None:
    offenders = [
        location
        for location, field in _interpolated_fields()
        if any(token in field for token in _RAW_BIOMETRIC_TOKENS)
    ]
    assert offenders == [], offenders


def test_no_stream_url_is_interpolated_without_masking() -> None:
    offenders = [
        location
        for location, field in _interpolated_fields()
        if any(token in field for token in _CREDENTIAL_TOKENS)
        and "mask_credentials" not in field
    ]
    assert offenders == [], offenders
