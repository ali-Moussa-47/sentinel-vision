from __future__ import annotations

import argparse
import time
import warnings
from dataclasses import replace
from pathlib import Path

import cv2

from sentinel_vision.bootstrap.email_alert_sink import EmailAlertSink
from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.communication.infrastructure.background_email_sender import (
    BackgroundEmailSender,
)
from sentinel_vision.communication.infrastructure.mail_settings import (
    MailSettings,
    MailSettingsError,
)
from sentinel_vision.communication.infrastructure.smtp_email_sender import SmtpEmailSender
from sentinel_vision.config import AppConfig
from sentinel_vision.recognition.application.face_tracking import FaceTracker
from sentinel_vision.recognition.application.match_alerter import MatchAlerter, MatchSink
from sentinel_vision.recognition.application.recognize_frame import FrameRecognition, RecognizeFrame
from sentinel_vision.recognition.application.snapshot_sink import SnapshotSink
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.domain.match_confirmation import MatchConfirmation
from sentinel_vision.recognition.domain.recognition_policy import RecognitionPolicy
from sentinel_vision.recognition.infrastructure.capture.local_snapshot_writer import (
    LocalSnapshotWriter,
)
from sentinel_vision.recognition.infrastructure.presentation import overlay
from sentinel_vision.recognition.infrastructure.presentation.status_screen import (
    StatusScreen,
    UserAction,
)
from sentinel_vision.recognition.infrastructure.vision.insightface_face_analyzer import (
    FaceAnalyzerInitializationError,
    InsightFaceFaceAnalyzer,
)
from sentinel_vision.recognition.infrastructure.watchlist.local_watchlist_loader import (
    LocalWatchlistLoader,
    WatchlistLoadError,
)

_QUIT_KEYS = {ord("q"), 27}


def run(config: AppConfig | None = None) -> None:
    config = config or AppConfig()
    warnings.filterwarnings("ignore", message="`estimate` is deprecated", category=FutureWarning)
    screen = StatusScreen(config.window_title)

    analyzer = _initialize_analyzer(config, screen)
    if analyzer is None:
        return

    quality_gate = FaceQualityGate(config.min_face_pixels, config.min_detection_score)
    watchlist = LocalWatchlistLoader(analyzer, quality_gate).load(Path(config.watchlist_path))
    print(f"Watchlist loaded: {watchlist.size} subjects")
    policy = RecognitionPolicy(config.recognition_threshold)
    recognize = RecognizeFrame(analyzer, watchlist, quality_gate, policy)

    alerter, email_sender = _build_alerter(config, _camera_label(config))
    try:
        _run_live_sessions(config, recognize, watchlist.size, screen, alerter)
    finally:
        if email_sender is not None:
            email_sender.close()
        cv2.destroyAllWindows()


def _initialize_analyzer(
    config: AppConfig, screen: StatusScreen
) -> InsightFaceFaceAnalyzer | None:
    while True:
        try:
            print("Loading recognition model (first run downloads it)...")
            return InsightFaceFaceAnalyzer(config)
        except FaceAnalyzerInitializationError as error:
            if screen.ask("Recognition engine unavailable", str(error)) is UserAction.QUIT:
                return None


def _run_live_sessions(
    config: AppConfig,
    recognize: RecognizeFrame,
    watchlist_size: int,
    screen: StatusScreen,
    alerter: MatchAlerter | None,
) -> None:
    while True:
        try:
            _run_live_session(config, recognize, watchlist_size, alerter)
            return
        except CameraError as error:
            if screen.ask("Camera unavailable", str(error)) is UserAction.QUIT:
                return


def _run_live_session(
    config: AppConfig,
    recognize: RecognizeFrame,
    watchlist_size: int,
    alerter: MatchAlerter | None,
) -> None:
    fps = 0.0
    provider_label = _provider_label(config)
    camera_label = _camera_label(config)
    tracker = FaceTracker(
        MatchConfirmation(config.confirm_frames),
        config.confirmation_window,
        config.track_iou_threshold,
        config.track_max_misses,
    )
    with open_frame_source(config) as camera:
        reconnects = camera.reconnect_count
        cv2.namedWindow(config.window_title, cv2.WINDOW_NORMAL)
        while True:
            start = time.perf_counter()

            frame = camera.read()
            if camera.reconnect_count != reconnects:
                tracker.reset()
                reconnects = camera.reconnect_count
            outcome = recognize(frame)
            if outcome.recognition_available:
                outcome = FrameRecognition.recognized(tuple(tracker.update(list(outcome.faces))))
                if alerter is not None:
                    alerter.process(frame, list(outcome.faces))
            overlay.render(frame, outcome, fps, watchlist_size, camera_label, provider_label)
            cv2.imshow(config.window_title, frame)

            if cv2.waitKey(1) & 0xFF in _QUIT_KEYS:
                return
            if cv2.getWindowProperty(config.window_title, cv2.WND_PROP_VISIBLE) < 1:
                return

            elapsed = time.perf_counter() - start
            if elapsed > 0:
                fps = (0.9 * fps + 0.1 / elapsed) if fps else 1.0 / elapsed


def _camera_label(config: AppConfig) -> str:
    return "NET" if config.camera_url else str(config.camera_index)


def _build_alerter(
    config: AppConfig, camera_label: str
) -> tuple[MatchAlerter | None, BackgroundEmailSender | None]:
    sinks: list[MatchSink] = []
    email_sender: BackgroundEmailSender | None = None
    location = config.camera_name or camera_label
    if config.capture_enabled:
        sinks.append(SnapshotSink(LocalSnapshotWriter(Path(config.capture_dir), location)))
    if config.notify_enabled:
        settings = MailSettings.from_env()
        email_sender = BackgroundEmailSender(SmtpEmailSender(settings))
        sinks.append(EmailAlertSink(email_sender, settings.recipient, location))
    if not sinks:
        return None, None
    return MatchAlerter(sinks, config.capture_cooldown_seconds), email_sender


def _provider_label(config: AppConfig) -> str:
    if not config.providers:
        return "CPU"
    return config.providers[0].removesuffix("ExecutionProvider").upper()


def main() -> None:
    parser = argparse.ArgumentParser(prog="sentinel-vision")
    parser.add_argument("--camera", type=int, help="camera index (default 0)")
    parser.add_argument(
        "--source", help="RTSP/stream URL (overrides --camera; or env SENTINEL_CAMERA_URL)"
    )
    parser.add_argument(
        "--capture", action="store_true", help="save a local snapshot on each confirmed match"
    )
    parser.add_argument(
        "--notify", action="store_true", help="email on each confirmed match (SMTP via env)"
    )
    arguments = parser.parse_args()
    config = resolve_camera_config(AppConfig(), arguments.camera, arguments.source)
    config = replace(
        config, capture_enabled=arguments.capture, notify_enabled=arguments.notify
    )
    try:
        run(config)
    except (WatchlistLoadError, MailSettingsError) as error:
        print(f"Sentinel Vision could not start: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
