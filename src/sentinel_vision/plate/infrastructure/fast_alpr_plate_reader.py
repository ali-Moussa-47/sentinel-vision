from __future__ import annotations

from typing import Any

import numpy as np

from sentinel_vision.plate.application.plate_reader import AnalyzedPlate, PlateReadingError
from sentinel_vision.plate.domain.plate_number import PlateNumber
from sentinel_vision.plate.domain.plate_reading import PlateReading
from sentinel_vision.plate.infrastructure.ocr_confidence import aggregate_confidence


class FastAlprPlateReader:
    def __init__(self, detector_model: str, ocr_model: str) -> None:
        try:
            from fast_alpr import ALPR

            self._alpr = ALPR(detector_model=detector_model, ocr_model=ocr_model)
        except Exception as exc:
            raise PlateReadingError(str(exc)) from exc

    def read(self, frame: np.ndarray) -> list[AnalyzedPlate]:
        try:
            results = self._alpr.predict(frame)
        except Exception as exc:
            raise PlateReadingError(str(exc)) from exc
        plates: list[AnalyzedPlate] = []
        for result in results:
            analyzed = _to_analyzed(result)
            if analyzed is not None:
                plates.append(analyzed)
        return plates


def _to_analyzed(result: Any) -> AnalyzedPlate | None:
    ocr = getattr(result, "ocr", None)
    text = getattr(ocr, "text", None) if ocr is not None else None
    if not text:
        return None
    try:
        plate = PlateNumber.normalize(text)
    except ValueError:
        return None
    confidence = aggregate_confidence(getattr(ocr, "confidence", None))
    box = result.detection.bounding_box
    return AnalyzedPlate(box.x1, box.y1, box.x2, box.y2, PlateReading(plate, confidence))
