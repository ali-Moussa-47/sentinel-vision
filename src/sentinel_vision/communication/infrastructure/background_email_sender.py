from __future__ import annotations

import queue
import threading
from collections.abc import Callable

from sentinel_vision.communication.application.email_sender import EmailSender, EmailSendingError
from sentinel_vision.communication.domain.email_message import EmailMessage


def _report(error: EmailSendingError) -> None:
    print(f"Notification failed: {error}")


class BackgroundEmailSender:
    def __init__(
        self,
        delegate: EmailSender,
        on_error: Callable[[EmailSendingError], None] = _report,
    ) -> None:
        self._delegate = delegate
        self._on_error = on_error
        self._queue: queue.Queue[EmailMessage | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, message: EmailMessage) -> None:
        self._queue.put(message)

    def close(self, timeout_seconds: float = 5.0) -> None:
        self._queue.put(None)
        self._thread.join(timeout_seconds)

    def _run(self) -> None:
        while True:
            message = self._queue.get()
            try:
                if message is None:
                    return
                self._delegate.send(message)
            except EmailSendingError as error:
                self._on_error(error)
            finally:
                self._queue.task_done()
