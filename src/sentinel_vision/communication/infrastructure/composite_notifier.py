from __future__ import annotations

from collections.abc import Sequence

from sentinel_vision.communication.application.alert_notifier import (
    AlertNotifier,
    NotificationError,
)
from sentinel_vision.communication.domain.alert import Alert


class CompositeNotifier:
    def __init__(self, notifiers: Sequence[AlertNotifier]) -> None:
        self._notifiers = tuple(notifiers)

    def notify(self, alert: Alert) -> None:
        failures: list[str] = []
        for notifier in self._notifiers:
            try:
                notifier.notify(alert)
            except NotificationError as error:
                failures.append(str(error))
        if failures:
            raise NotificationError("; ".join(failures))
