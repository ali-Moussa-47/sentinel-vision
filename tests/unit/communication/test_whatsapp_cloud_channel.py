from __future__ import annotations

import pytest

from sentinel_vision.communication.application.alert_notifier import NotificationError
from sentinel_vision.communication.domain.alert import Alert, AlertImage
from sentinel_vision.communication.infrastructure.http_client import HttpError, HttpResponse
from sentinel_vision.communication.infrastructure.whatsapp_cloud_channel import (
    WhatsAppCloudChannel,
    WhatsAppSettings,
)

_SETTINGS = WhatsAppSettings("token", "123", "+23599", "v21.0")


class _FakeHttp:
    def __init__(self, *responses: HttpResponse) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, object]]] = []

    def post_json(self, url, headers, payload):  # type: ignore[no-untyped-def]
        self.calls.append(("json", url, payload))
        return self._responses.pop(0)

    def post_multipart(self, url, headers, fields, files):  # type: ignore[no-untyped-def]
        self.calls.append(("multipart", url, fields))
        return self._responses.pop(0)


class _RaisingHttp:
    def post_json(self, url, headers, payload):  # type: ignore[no-untyped-def]
        raise HttpError("network down")

    def post_multipart(self, url, headers, fields, files):  # type: ignore[no-untyped-def]
        raise HttpError("network down")


def test_text_only_alert_sends_one_message() -> None:
    http = _FakeHttp(HttpResponse(200, b"{}"))
    WhatsAppCloudChannel(http, _SETTINGS).notify(Alert("T", "B"))
    assert len(http.calls) == 1
    kind, url, payload = http.calls[0]
    assert kind == "json"
    assert url.endswith("/messages")
    assert payload["type"] == "text"


def test_image_alert_uploads_media_then_sends() -> None:
    http = _FakeHttp(HttpResponse(200, b'{"id": "MID"}'), HttpResponse(200, b"{}"))
    alert = Alert("T", "B", AlertImage("p.jpg", "image/jpeg", b"\xff\xd8\xff"))
    WhatsAppCloudChannel(http, _SETTINGS).notify(alert)
    assert [call[0] for call in http.calls] == ["multipart", "json"]
    assert http.calls[0][1].endswith("/media")
    assert http.calls[1][2]["image"] == {"id": "MID", "caption": "T\nB"}


def test_api_error_status_raises_notification_error() -> None:
    http = _FakeHttp(HttpResponse(401, b'{"error": "bad token"}'))
    with pytest.raises(NotificationError):
        WhatsAppCloudChannel(http, _SETTINGS).notify(Alert("T", "B"))


def test_transport_error_raises_notification_error() -> None:
    with pytest.raises(NotificationError):
        WhatsAppCloudChannel(_RaisingHttp(), _SETTINGS).notify(Alert("T", "B"))
