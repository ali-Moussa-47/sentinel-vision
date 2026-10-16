from __future__ import annotations

from sentinel_vision.communication.application.alert_notifier import NotificationError
from sentinel_vision.communication.domain.alert import Alert
from sentinel_vision.communication.infrastructure.background_notifier import BackgroundNotifier
from sentinel_vision.communication.infrastructure.composite_notifier import CompositeNotifier

_ALERT = Alert("T", "B")


class _Recording:
    def __init__(self) -> None:
        self.count = 0

    def notify(self, alert: Alert) -> None:
        self.count += 1


class _Failing:
    def notify(self, alert: Alert) -> None:
        raise NotificationError("down")


def test_composite_fans_out_to_every_channel() -> None:
    a, b = _Recording(), _Recording()
    CompositeNotifier([a, b]).notify(_ALERT)
    assert (a.count, b.count) == (1, 1)


def test_composite_tries_all_then_aggregates_failures() -> None:
    good = _Recording()
    composite = CompositeNotifier([_Failing(), good])
    try:
        composite.notify(_ALERT)
    except NotificationError:
        pass
    assert good.count == 1


def test_background_notifier_delivers() -> None:
    sink = _Recording()
    notifier = BackgroundNotifier(sink)
    notifier.notify(_ALERT)
    notifier.close()
    assert sink.count == 1


def test_background_notifier_reports_failure() -> None:
    errors: list[NotificationError] = []
    notifier = BackgroundNotifier(_Failing(), on_error=errors.append)
    notifier.notify(_ALERT)
    notifier.close()
    assert len(errors) == 1
