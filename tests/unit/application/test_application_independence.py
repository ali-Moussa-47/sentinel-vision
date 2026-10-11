from __future__ import annotations

from pathlib import Path

from sentinel_vision.recognition import application

_APPLICATION_SOURCES = tuple(Path(application.__file__).parent.glob("*.py"))


def test_application_has_source_files() -> None:
    assert _APPLICATION_SOURCES


def test_application_never_imports_infrastructure() -> None:
    for source in _APPLICATION_SOURCES:
        assert "infrastructure" not in source.read_text()
