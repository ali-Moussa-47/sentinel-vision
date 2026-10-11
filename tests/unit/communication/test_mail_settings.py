from __future__ import annotations

import pytest

from sentinel_vision.communication.infrastructure.mail_settings import (
    MailSettings,
    MailSettingsError,
)

_REQUIRED = {
    "SENTINEL_SMTP_HOST": "smtp.example.com",
    "SENTINEL_SMTP_FROM": "from@example.com",
    "SENTINEL_SMTP_TO": "to@example.com",
}


def _set(monkeypatch: pytest.MonkeyPatch, env: dict[str, str]) -> None:
    for key in (
        "SENTINEL_SMTP_HOST",
        "SENTINEL_SMTP_FROM",
        "SENTINEL_SMTP_TO",
        "SENTINEL_SMTP_PORT",
        "SENTINEL_SMTP_USER",
        "SENTINEL_SMTP_PASSWORD",
        "SENTINEL_SMTP_TLS",
    ):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)


def test_settings_are_built_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch, {**_REQUIRED, "SENTINEL_SMTP_PORT": "2525"})
    settings = MailSettings.from_env()
    assert settings.host == "smtp.example.com"
    assert settings.port == 2525
    assert settings.recipient.value == "to@example.com"


def test_missing_required_variable_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch, {"SENTINEL_SMTP_HOST": "smtp.example.com"})
    with pytest.raises(MailSettingsError):
        MailSettings.from_env()


def test_invalid_recipient_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch, {**_REQUIRED, "SENTINEL_SMTP_TO": "not-an-email"})
    with pytest.raises(MailSettingsError):
        MailSettings.from_env()
