from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np
import onnxruntime as ort

from sentinel_vision.detection.application.object_detector import ObjectDetectionError
from sentinel_vision.detection.domain.detected_object import DetectedObject
from sentinel_vision.detection.infrastructure.yolox_postprocess import decode, nms

_COCO_CLASSES = (
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
)

DEFAULT_LABELS = frozenset({"person", "bicycle", "car", "motorcycle", "bus", "truck"})


class YoloxOnnxObjectDetector:
    def __init__(
        self,
        model_path: str,
        score_threshold: float,
        nms_threshold: float,
        providers: Sequence[str],
        labels: frozenset[str] = DEFAULT_LABELS,
    ) -> None:
        try:
            self._session = ort.InferenceSession(model_path, providers=list(providers))
        except Exception as exc:
            raise ObjectDetectionError(str(exc)) from exc
        model_input = self._session.get_inputs()[0]
        self._input_name = model_input.name
        self._input_height = int(model_input.shape[2])
        self._input_width = int(model_input.shape[3])
        self._score_threshold = score_threshold
        self._nms_threshold = nms_threshold
        self._labels = labels

    def detect(self, frame: np.ndarray) -> list[DetectedObject]:
        tensor, ratio = self._preprocess(frame)
        try:
            raw = self._session.run(None, {self._input_name: tensor})[0][0]
        except Exception as exc:
            raise ObjectDetectionError(str(exc)) from exc
        boxes, scores, class_ids = decode(raw, self._input_height, self._input_width)
        confident = scores >= self._score_threshold
        return self._to_objects(boxes[confident] / ratio, scores[confident], class_ids[confident], frame.shape[:2])

    def _preprocess(self, frame: np.ndarray) -> tuple[np.ndarray, float]:
        height, width = frame.shape[:2]
        ratio = min(self._input_height / height, self._input_width / width)
        resized = cv2.resize(frame, (round(width * ratio), round(height * ratio)), interpolation=cv2.INTER_LINEAR)
        padded = np.full((self._input_height, self._input_width, 3), 114, dtype=np.uint8)
        padded[: resized.shape[0], : resized.shape[1]] = resized
        tensor = np.ascontiguousarray(padded.transpose(2, 0, 1)[None], dtype=np.float32)
        return tensor, ratio

    def _to_objects(
        self,
        boxes: np.ndarray,
        scores: np.ndarray,
        class_ids: np.ndarray,
        frame_shape: tuple[int, int],
    ) -> list[DetectedObject]:
        height, width = frame_shape
        detected: list[DetectedObject] = []
        for class_id in np.unique(class_ids):
            label = _COCO_CLASSES[int(class_id)]
            if label not in self._labels:
                continue
            selected = np.where(class_ids == class_id)[0]
            for keep in nms(boxes[selected], scores[selected], self._nms_threshold):
                index = selected[keep]
                box = _clamp(boxes[index], width, height)
                if box is not None:
                    detected.append(DetectedObject(label, *box, float(scores[index])))
        return detected


def _clamp(box: np.ndarray, width: int, height: int) -> tuple[int, int, int, int] | None:
    x1 = min(max(round(float(box[0])), 0), width)
    y1 = min(max(round(float(box[1])), 0), height)
    x2 = min(max(round(float(box[2])), 0), width)
    y2 = min(max(round(float(box[3])), 0), height)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2
