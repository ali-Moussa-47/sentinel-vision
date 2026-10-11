from __future__ import annotations

from pathlib import Path

from sentinel_vision.recognition import domain

_DOMAIN_SOURCES = tuple(Path(domain.__file__).parent.glob("*.py"))


def test_domain_has_source_files() -> None:
    assert _DOMAIN_SOURCES


def test_domain_never_imports_opencv() -> None:
    for source in _DOMAIN_SOURCES:
        assert "cv2" not in source.read_text()


def test_domain_never_imports_insightface() -> None:
    for source in _DOMAIN_SOURCES:
        assert "insightface" not in source.read_text()
