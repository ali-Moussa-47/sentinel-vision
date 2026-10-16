from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from sentinel_vision.config import AppConfig

_TUPLE_FIELDS = frozenset({"det_size", "providers"})


class ConfigFileError(RuntimeError):
    pass


def load_app_config(path: Path) -> AppConfig:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigFileError(f"cannot read config {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigFileError("config file must contain a JSON object")
    known = {field.name for field in fields(AppConfig)}
    unknown = sorted(set(raw) - known)
    if unknown:
        raise ConfigFileError(f"unknown config keys: {unknown}")
    data: dict[str, object] = {
        key: (tuple(value) if key in _TUPLE_FIELDS and isinstance(value, list) else value)
        for key, value in raw.items()
    }
    try:
        return AppConfig(**data)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ConfigFileError(f"invalid config: {error}") from error
