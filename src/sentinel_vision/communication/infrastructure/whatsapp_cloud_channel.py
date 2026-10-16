from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass

from sentinel_vision.communication.application.alert_notifier import NotificationError
from sentinel_vision.communication.domain.alert import Alert, AlertImage
from sentinel_vision.communication.infrastructure.http_client import (
    HttpClient,
    HttpError,
    HttpResponse,
)


class WhatsAppSettingsError(RuntimeError):
    pass


@dataclass(frozen=True)
class WhatsAppSettings:
    access_token: str
    phone_number_id: str
    recipient: str
    api_version: str = "v21.0"

    @classmethod
    def from_env(cls) -> WhatsAppSettings:
        token = os.environ.get("SENTINEL_WHATSAPP_TOKEN")
        phone_id = os.environ.get("SENTINEL_WHATSAPP_PHONE_ID")
        recipient = os.environ.get("SENTINEL_WHATSAPP_TO")
        if not token or not phone_id or not recipient:
            raise WhatsAppSettingsError(
                "set SENTINEL_WHATSAPP_TOKEN, SENTINEL_WHATSAPP_PHONE_ID and SENTINEL_WHATSAPP_TO"
            )
        return cls(
            access_token=token,
            phone_number_id=phone_id,
            recipient=recipient,
            api_version=os.environ.get("SENTINEL_WHATSAPP_API_VERSION", "v21.0"),
        )


class WhatsAppCloudChannel:
    def __init__(self, http: HttpClient, settings: WhatsAppSettings) -> None:
        self._http = http
        self._settings = settings
        base = f"https://graph.facebook.com/{settings.api_version}/{settings.phone_number_id}"
        self._media_url = f"{base}/media"
        self._messages_url = f"{base}/messages"

    def notify(self, alert: Alert) -> None:
        if alert.image is not None:
            payload = self._image_payload(alert, self._upload(alert.image))
        else:
            payload = self._text_payload(alert)
        response = self._send(lambda: self._http.post_json(self._messages_url, self._auth(), payload))
        self._ensure_ok(response)

    def _upload(self, image: AlertImage) -> str:
        response = self._send(
            lambda: self._http.post_multipart(
                self._media_url,
                self._auth(),
                {"messaging_product": "whatsapp", "type": image.content_type},
                {"file": (image.filename, image.content_type, image.content)},
            )
        )
        self._ensure_ok(response)
        media_id = json.loads(response.body).get("id")
        if not media_id:
            raise NotificationError(f"WhatsApp media upload returned no id: {response.body!r}")
        return str(media_id)

    def _text_payload(self, alert: Alert) -> dict[str, object]:
        return {
            "messaging_product": "whatsapp",
            "to": self._settings.recipient,
            "type": "text",
            "text": {"body": _caption(alert)},
        }

    def _image_payload(self, alert: Alert, media_id: str) -> dict[str, object]:
        return {
            "messaging_product": "whatsapp",
            "to": self._settings.recipient,
            "type": "image",
            "image": {"id": media_id, "caption": _caption(alert)},
        }

    def _send(self, call: Callable[[], HttpResponse]) -> HttpResponse:
        try:
            return call()
        except HttpError as error:
            raise NotificationError(str(error)) from error

    def _ensure_ok(self, response: HttpResponse) -> None:
        if response.status >= 300:
            raise NotificationError(
                f"WhatsApp API returned {response.status}: {response.body!r}"
            )

    def _auth(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._settings.access_token}"}


def _caption(alert: Alert) -> str:
    return f"{alert.title}\n{alert.body}"
