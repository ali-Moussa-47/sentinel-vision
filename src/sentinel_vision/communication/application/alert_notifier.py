from __future__ import annotations

from typing import Protocol

from sentinel_vision.communication.domain.alert import Alert


class NotificationError(RuntimeError):
    pass


class AlertNotifier(Protocol):
    def notify(self, alert: Alert) -> None: ...
