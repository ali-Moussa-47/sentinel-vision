from __future__ import annotations

import argparse
import time
import warnings
from dataclasses import replace
from pathlib import Path

import cv2
import numpy as np

from sentinel_vision.bootstrap.capture_retention import CaptureRetention
from sentinel_vision.bootstrap.email_alert_sink import EmailAlertSink
from sentinel_vision.bootstrap.frame_source import (
    CameraError,
    open_frame_source,
    resolve_camera_config,
)
from sentinel_vision.bootstrap.notifying_sinks import NotifyingMatchSink, NotifyingPlateSink
from sentinel_vision.bootstrap.plate_email_alert_sink import PlateEmailAlertSink
from sentinel_vision.communication.application.alert_notifier import AlertNotifier
from sentinel_vision.communication.infrastructure.background_email_sender import (
    BackgroundEmailSender,
)
from sentinel_vision.communication.infrastructure.background_notifier import BackgroundNotifier
from sentinel_vision.communication.infrastructure.composite_notifier import CompositeNotifier
from sentinel_vision.communication.infrastructure.http_client import UrllibHttpClient
from sentinel_vision.communication.infrastructure.http_webhook_channel import HttpWebhookChannel
from sentinel_vision.communication.infrastructure.mail_settings import (
    MailSettings,
    MailSettingsError,
)
from sentinel_vision.communication.infrastructure.smtp_email_sender import SmtpEmailSender
from sentinel_vision.communication.infrastructure.whatsapp_cloud_channel import (
    WhatsAppCloudChannel,
    WhatsAppSettings,
    WhatsAppSettingsError,
)
from sentinel_vision.config import AppConfig
from sentinel_vision.detection.application.object_detector import (
    ObjectDetectionError,
    ObjectDetector,
)
from sentinel_vision.detection.application.object_tracking import ObjectTracker
from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.domain.tracked_object import TrackedObject
from sentinel_vision.detection.infrastructure.presentation import object_overlay
from sentinel_vision.detection.infrastructure.yolox_onnx_detector import YoloxOnnxObjectDetector
from sentinel_vision.plate.application.plate_alerter import PlateAlerter, PlateSink
from sentinel_vision.plate.application.plate_reader import PlateReadingError
from sentinel_vision.plate.application.plate_snapshot_sink import PlateSnapshotSink
from sentinel_vision.plate.application.recognize_plate import RecognizePlate
from sentinel_vision.plate.application.vehicle_plate_reader import VehiclePlateReader
from sentinel_vision.plate.domain.plate_reading_policy import PlateReadingPolicy
from sentinel_vision.plate.domain.plate_recognition_result import PlateRecognitionResult
from sentinel_vision.plate.infrastructure.capture.local_plate_snapshot_writer import (
    LocalPlateSnapshotWriter,
)
from sentinel_vision.plate.infrastructure.fast_alpr_plate_reader import FastAlprPlateReader
from sentinel_vision.plate.infrastructure.file_plate_watchlist_loader import load_plate_watchlist
from sentinel_vision.plate.infrastructure.presentation import plate_overlay
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
_VEHICLE_LABELS = frozenset({"car", "motorcycle", "bus", "truck"})
_PURGE_INTERVAL_SECONDS = 300.0


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

    detector = _initialize_detector(config)
    plate_reader = _initialize_vehicle_plate_reader(config)
    location = config.camera_name or _camera_label(config)
    mail_settings = MailSettings.from_env() if config.notify_enabled else None
    email_sender = (
        BackgroundEmailSender(SmtpEmailSender(mail_settings)) if mail_settings is not None else None
    )
    notifier = _build_notifier(config)
    alerter = _build_face_alerter(config, location, email_sender, mail_settings, notifier)
    plate_alerter = _build_plate_alerter(config, location, email_sender, mail_settings, notifier)
    try:
        _run_live_sessions(
            config, recognize, watchlist.size, screen, alerter, detector, plate_reader, plate_alerter
        )
    finally:
        if email_sender is not None:
            email_sender.close()
        if notifier is not None:
            notifier.close()
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
    detector: ObjectDetector | None,
    plate_reader: VehiclePlateReader | None,
    plate_alerter: PlateAlerter | None,
) -> None:
    while True:
        try:
            _run_live_session(
                config, recognize, watchlist_size, alerter, detector, plate_reader, plate_alerter
            )
            return
        except CameraError as error:
            if screen.ask("Camera unavailable", str(error)) is UserAction.QUIT:
                return


def _run_live_session(
    config: AppConfig,
    recognize: RecognizeFrame,
    watchlist_size: int,
    alerter: MatchAlerter | None,
    detector: ObjectDetector | None,
    plate_reader: VehiclePlateReader | None,
    plate_alerter: PlateAlerter | None,
) -> None:
    fps = 0.0
    provider_label = _provider_label(config)
    camera_label = _camera_label(config)
    tracker = FaceTracker(
        MatchConfirmation(config.confirm_frames),
        config.confirmation_window,
        config.track_iou_threshold,
        config.track_max_misses,
        config.box_smoothing,
    )
    object_tracker = ObjectTracker(config.track_iou_threshold, config.track_max_misses)
    retention = _build_retention(config)
    last_purge = _purge(retention, time.perf_counter())
    with open_frame_source(config) as camera:
        reconnects = camera.reconnect_count
        cv2.namedWindow(config.window_title, cv2.WINDOW_NORMAL)
        while True:
            start = time.perf_counter()
            last_purge = _purge_if_due(retention, start, last_purge)

            frame = camera.read()
            if camera.reconnect_count != reconnects:
                tracker.reset()
                object_tracker.reset()
                if plate_reader is not None:
                    plate_reader.reset()
                reconnects = camera.reconnect_count
            objects, detection_ok = _detect(detector, frame)
            tracked = object_tracker.update(objects)
            plate_results, plates_ok = _read_vehicle_plates(plate_reader, frame, tracked)
            plate_entries = _plate_entries(tracked, plate_results)
            outcome = recognize(frame)
            if outcome.recognition_available:
                outcome = FrameRecognition.recognized(tuple(tracker.update(list(outcome.faces))))
                if alerter is not None:
                    alerter.process(frame, list(outcome.faces))
            if plate_alerter is not None:
                plate_alerter.process(frame, plate_entries)
            object_overlay.draw_tracked(frame, tracked)
            plate_overlay.draw_on_vehicles(frame, plate_entries)
            status = _capability_status(
                _object_status(config.detection_enabled, detector, detection_ok, len(tracked)),
                _plate_status(config.plates_enabled, plate_reader, plates_ok, len(plate_results)),
            )
            overlay.render(frame, outcome, fps, watchlist_size, camera_label, provider_label, status)
            cv2.imshow(config.window_title, frame)

            if cv2.waitKey(1) & 0xFF in _QUIT_KEYS:
                return
            if cv2.getWindowProperty(config.window_title, cv2.WND_PROP_VISIBLE) < 1:
                return

            elapsed = time.perf_counter() - start
            if elapsed > 0:
                fps = (0.9 * fps + 0.1 / elapsed) if fps else 1.0 / elapsed


def _initialize_detector(config: AppConfig) -> ObjectDetector | None:
    if not config.detection_enabled:
        return None
    try:
        return YoloxOnnxObjectDetector(
            config.detection_model_path,
            config.detection_score_threshold,
            config.detection_nms_threshold,
            config.providers,
        )
    except (ObjectDetectionError, FileNotFoundError) as error:
        print(f"Object detection unavailable: {error}")
        return None


def _detect(detector: ObjectDetector | None, frame: np.ndarray) -> tuple[list[DetectedObject], bool]:
    if detector is None:
        return [], True
    try:
        return detector.detect(frame), True
    except ObjectDetectionError:
        return [], False


def _object_status(
    enabled: bool, detector: ObjectDetector | None, available: bool, count: int
) -> str | None:
    if not enabled:
        return None
    if detector is None or not available:
        return "DETECT UNAVAILABLE"
    return f"DETECT {count}"


def _initialize_vehicle_plate_reader(config: AppConfig) -> VehiclePlateReader | None:
    if not config.plates_enabled:
        return None
    try:
        reader = FastAlprPlateReader(config.plate_detector_model, config.plate_ocr_model)
    except PlateReadingError as error:
        print(f"Plate reading unavailable: {error}")
        return None
    watchlist = load_plate_watchlist(Path(config.plate_watchlist_path))
    print(f"Plate watchlist loaded: {watchlist.size} plates")
    recognize = RecognizePlate(reader, watchlist, PlateReadingPolicy(config.plate_min_confidence))
    return VehiclePlateReader(
        recognize,
        config.plate_burst_attempts,
        config.plate_read_interval,
        config.plate_confirm_count,
        config.plate_confirm_window,
    )


def _read_vehicle_plates(
    plate_reader: VehiclePlateReader | None, frame: np.ndarray, tracked: list[TrackedObject]
) -> tuple[dict[int, PlateRecognitionResult], bool]:
    if plate_reader is None:
        return {}, True
    crops = [
        (vehicle.track_id, _crop(frame, vehicle.observation))
        for vehicle in tracked
        if vehicle.observation.label in _VEHICLE_LABELS
    ]
    try:
        return plate_reader.update(crops), True
    except PlateReadingError:
        return {}, False


def _crop(frame: np.ndarray, obj: DetectedObject) -> np.ndarray:
    return frame[obj.y1 : obj.y2, obj.x1 : obj.x2]


def _plate_entries(
    tracked: list[TrackedObject], plate_results: dict[int, PlateRecognitionResult]
) -> list[tuple[tuple[int, int, int, int], PlateRecognitionResult]]:
    entries: list[tuple[tuple[int, int, int, int], PlateRecognitionResult]] = []
    for vehicle in tracked:
        result = plate_results.get(vehicle.track_id)
        if result is not None:
            box = vehicle.observation
            entries.append(((box.x1, box.y1, box.x2, box.y2), result))
    return entries


def _plate_status(
    enabled: bool, plate_reader: VehiclePlateReader | None, available: bool, count: int
) -> str | None:
    if not enabled:
        return None
    if plate_reader is None or not available:
        return "PLATES UNAVAILABLE"
    return f"PLATES {count}"


def _capability_status(*segments: str | None) -> str | None:
    present = [segment for segment in segments if segment]
    return "   ".join(present) if present else None


def _camera_label(config: AppConfig) -> str:
    return "NET" if config.camera_url else str(config.camera_index)


def _build_notifier(config: AppConfig) -> BackgroundNotifier | None:
    channels: list[AlertNotifier] = []
    http = UrllibHttpClient()
    if config.whatsapp_enabled:
        channels.append(WhatsAppCloudChannel(http, WhatsAppSettings.from_env()))
    if config.webhook_url:
        channels.append(HttpWebhookChannel(http, config.webhook_url))
    if not channels:
        return None
    return BackgroundNotifier(CompositeNotifier(channels))


def _build_face_alerter(
    config: AppConfig,
    location: str,
    email_sender: BackgroundEmailSender | None,
    mail_settings: MailSettings | None,
    notifier: AlertNotifier | None,
) -> MatchAlerter | None:
    sinks: list[MatchSink] = []
    if config.capture_enabled:
        sinks.append(SnapshotSink(LocalSnapshotWriter(Path(config.capture_dir), location)))
    if email_sender is not None and mail_settings is not None:
        sinks.append(EmailAlertSink(email_sender, mail_settings.recipient, location))
    if notifier is not None:
        sinks.append(NotifyingMatchSink(notifier, location))
    return MatchAlerter(sinks, config.capture_cooldown_seconds) if sinks else None


def _build_plate_alerter(
    config: AppConfig,
    location: str,
    email_sender: BackgroundEmailSender | None,
    mail_settings: MailSettings | None,
    notifier: AlertNotifier | None,
) -> PlateAlerter | None:
    if not config.plates_enabled:
        return None
    sinks: list[PlateSink] = []
    if config.capture_enabled:
        writer = LocalPlateSnapshotWriter(Path(config.capture_dir) / "plates", location)
        sinks.append(PlateSnapshotSink(writer))
    if email_sender is not None and mail_settings is not None:
        sinks.append(PlateEmailAlertSink(email_sender, mail_settings.recipient, location))
    if notifier is not None:
        sinks.append(NotifyingPlateSink(notifier, location))
    return PlateAlerter(sinks, config.capture_cooldown_seconds) if sinks else None


def _build_retention(config: AppConfig) -> CaptureRetention | None:
    if not config.capture_enabled or config.capture_retention_seconds <= 0:
        return None
    return CaptureRetention(Path(config.capture_dir), config.capture_retention_seconds)


def _purge(retention: CaptureRetention | None, moment: float) -> float:
    if retention is not None:
        retention.purge()
    return moment


def _purge_if_due(retention: CaptureRetention | None, moment: float, last_purge: float) -> float:
    if retention is None or moment - last_purge < _PURGE_INTERVAL_SECONDS:
        return last_purge
    retention.purge()
    return moment


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
    parser.add_argument(
        "--detect", action="store_true", help="also detect persons/vehicles (YOLOX)"
    )
    parser.add_argument(
        "--plates", action="store_true", help="read license plates on vehicles (enables detection)"
    )
    parser.add_argument(
        "--whatsapp", action="store_true", help="push alerts via WhatsApp Cloud API (env config)"
    )
    parser.add_argument("--webhook", help="push alerts as JSON POST to this URL")
    arguments = parser.parse_args()
    config = resolve_camera_config(AppConfig(), arguments.camera, arguments.source)
    config = replace(
        config,
        capture_enabled=arguments.capture,
        notify_enabled=arguments.notify,
        detection_enabled=arguments.detect or arguments.plates,
        plates_enabled=arguments.plates,
        whatsapp_enabled=arguments.whatsapp,
        webhook_url=arguments.webhook or "",
    )
    try:
        run(config)
    except (WatchlistLoadError, MailSettingsError, WhatsAppSettingsError) as error:
        print(f"Sentinel Vision could not start: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
