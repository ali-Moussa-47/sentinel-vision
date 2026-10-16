from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinel_vision.bootstrap.config_file import ConfigFileError, load_app_config


def _write(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "cam.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_loads_overrides_and_keeps_defaults(tmp_path: Path) -> None:
    config = load_app_config(_write(tmp_path, {"camera_url": "rtsp://x/s", "plate_confirm_count": 2}))
    assert config.camera_url == "rtsp://x/s"
    assert config.plate_confirm_count == 2
    assert config.recognition_threshold == 0.45


def test_list_fields_are_coerced_to_tuples(tmp_path: Path) -> None:
    config = load_app_config(_write(tmp_path, {"det_size": [640, 640], "providers": ["CPUExecutionProvider"]}))
    assert config.det_size == (640, 640)
    assert config.providers == ("CPUExecutionProvider",)


def test_unknown_key_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileError):
        load_app_config(_write(tmp_path, {"recognistion_threshold": 0.5}))


def test_invalid_value_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileError):
        load_app_config(_write(tmp_path, {"recognition_threshold": 5.0}))


def test_plates_without_detection_in_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileError):
        load_app_config(_write(tmp_path, {"plates_enabled": True}))


def test_malformed_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigFileError):
        load_app_config(path)
