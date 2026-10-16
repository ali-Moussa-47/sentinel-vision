from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    camera_url: str | None = None
    frame_width: int = 1280
    frame_height: int = 720

    stream_timeout_ms: int = 5000
    reconnect_attempts: int = 3
    reconnect_backoff: float = 1.0

    model_name: str = "buffalo_s"
    det_size: tuple[int, int] = (320, 320)
    det_threshold: float = 0.5

    recognition_threshold: float = 0.45
    min_face_pixels: int = 112
    min_detection_score: float = 0.65

    confirm_frames: int = 3
    confirmation_window: int = 5
    track_iou_threshold: float = 0.3
    track_max_misses: int = 15
    box_smoothing: float = 0.5

    watchlist_path: str = "data/watchlist"

    detection_enabled: bool = False
    detection_model_path: str = "models/yolox_nano.onnx"
    detection_score_threshold: float = 0.3
    detection_nms_threshold: float = 0.45

    plates_enabled: bool = False
    plate_detector_model: str = "yolo-v9-t-384-license-plate-end2end"
    plate_ocr_model: str = "cct-xs-v2-global-model"
    plate_min_confidence: float = 0.6
    plate_watchlist_path: str = "data/plate_watchlist.txt"
    plate_burst_attempts: int = 8
    plate_read_interval: int = 5
    plate_confirm_count: int = 3
    plate_confirm_window: int = 5

    capture_enabled: bool = False
    capture_dir: str = "data/captures"
    capture_cooldown_seconds: float = 30.0
    capture_retention_seconds: float = 0.0
    camera_name: str = ""

    notify_enabled: bool = False
    whatsapp_enabled: bool = False
    webhook_url: str = ""

    providers: tuple[str, ...] = ("CPUExecutionProvider",)
    window_title: str = "Sentinel Vision"
    headless: bool = False

    def __post_init__(self) -> None:
        if self.camera_index < 0:
            raise ValueError("camera_index must be >= 0")
        if self.frame_width < 1 or self.frame_height < 1:
            raise ValueError("frame dimensions must be positive")
        if not 0.0 <= self.det_threshold <= 1.0:
            raise ValueError("det_threshold must be within [0, 1]")
        if self.det_size[0] < 1 or self.det_size[1] < 1:
            raise ValueError("det_size must be positive")
        if not -1.0 <= self.recognition_threshold <= 1.0:
            raise ValueError("recognition_threshold must be within [-1, 1]")
        if self.min_face_pixels < 1:
            raise ValueError("min_face_pixels must be >= 1")
        if not 0.0 <= self.min_detection_score <= 1.0:
            raise ValueError("min_detection_score must be within [0, 1]")
        if self.confirm_frames < 1:
            raise ValueError("confirm_frames must be >= 1")
        if self.confirmation_window < self.confirm_frames:
            raise ValueError("confirmation_window must be >= confirm_frames")
        if not 0.0 <= self.track_iou_threshold <= 1.0:
            raise ValueError("track_iou_threshold must be within [0, 1]")
        if self.track_max_misses < 0:
            raise ValueError("track_max_misses must be >= 0")
        if not 0.0 <= self.box_smoothing < 1.0:
            raise ValueError("box_smoothing must be within [0, 1)")
        if self.reconnect_attempts < 0:
            raise ValueError("reconnect_attempts must be >= 0")
        if self.reconnect_backoff < 0:
            raise ValueError("reconnect_backoff must be >= 0")
        if self.stream_timeout_ms < 0:
            raise ValueError("stream_timeout_ms must be >= 0")
        if self.capture_cooldown_seconds < 0:
            raise ValueError("capture_cooldown_seconds must be >= 0")
        if self.capture_retention_seconds < 0:
            raise ValueError("capture_retention_seconds must be >= 0")
        if not 0.0 <= self.detection_score_threshold <= 1.0:
            raise ValueError("detection_score_threshold must be within [0, 1]")
        if not 0.0 <= self.detection_nms_threshold <= 1.0:
            raise ValueError("detection_nms_threshold must be within [0, 1]")
        if not 0.0 <= self.plate_min_confidence <= 1.0:
            raise ValueError("plate_min_confidence must be within [0, 1]")
        if self.plate_burst_attempts < 1:
            raise ValueError("plate_burst_attempts must be >= 1")
        if self.plate_read_interval < 1:
            raise ValueError("plate_read_interval must be >= 1")
        if self.plate_confirm_count < 1:
            raise ValueError("plate_confirm_count must be >= 1")
        if self.plate_confirm_window < self.plate_confirm_count:
            raise ValueError("plate_confirm_window must be >= plate_confirm_count")
        if self.plates_enabled and not self.detection_enabled:
            raise ValueError("plates_enabled requires detection_enabled")
