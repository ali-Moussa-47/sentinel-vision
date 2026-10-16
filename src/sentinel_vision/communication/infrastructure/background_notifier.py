from __future__ import annotations

import queue
import threading
from collections.abc import Callable

from sentinel_vision.communication.application.alert_notifier import (
    AlertNotifier,
    NotificationError,
)
from sentinel_vision.communication.domain.alert import Alert


def _report(error: NotificationError) -> None:
    print(f"Alert notification failed: {error}")


class BackgroundNotifier:
    def __init__(
        self,
        delegate: AlertNotifier,
        on_error: Callable[[NotificationError], None] = _report,
    ) -> None:
        self._delegate = delegate
        self._on_error = on_error
        self._queue: queue.Queue[Alert | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def notify(self, alert: Alert) -> None:
        self._queue.put(alert)

    def close(self, timeout_seconds: float = 5.0) -> None:
        self._queue.put(None)
        self._thread.join(timeout_seconds)

    def _run(self) -> None:
        while True:
            alert = self._queue.get()
            try:
                if alert is None:
                    return
                self._delegate.notify(alert)
            except NotificationError as error:
                self._on_error(error)
            finally:
                self._queue.task_done()
