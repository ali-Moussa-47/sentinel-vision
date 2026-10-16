from __future__ import annotations

import base64

from sentinel_vision.communication.application.alert_notifier import NotificationError
from sentinel_vision.communication.domain.alert import Alert
from sentinel_vision.communication.infrastructure.http_client import HttpClient, HttpError


class HttpWebhookChannel:
    def __init__(self, http: HttpClient, url: str, headers: dict[str, str] | None = None) -> None:
        self._http = http
        self._url = url
        self._headers = headers or {}

    def notify(self, alert: Alert) -> None:
        payload: dict[str, object] = {"title": alert.title, "body": alert.body}
        if alert.image is not None:
            payload["image_base64"] = base64.b64encode(alert.image.content).decode("ascii")
            payload["image_name"] = alert.image.filename
        try:
            response = self._http.post_json(self._url, self._headers, payload)
        except HttpError as error:
            raise NotificationError(str(error)) from error
        if response.status >= 300:
            raise NotificationError(f"webhook returned {response.status}: {response.body!r}")
