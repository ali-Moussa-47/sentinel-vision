from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from sentinel_vision.recognition.application.face_analyzer import AnalyzedFace, FaceAnalysisError
from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_observation import FaceObservation
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.infrastructure.watchlist.local_watchlist_loader import (
    LocalWatchlistLoader,
    WatchlistLoadError,
)

_GATE = FaceQualityGate(min_face_pixels=112, min_detection_score=0.65)
_RELIABLE = AnalyzedFace(FaceObservation(0, 0, 120, 120, 0.9), FaceEmbedding((1.0, 0.0)))
_TOO_FAR = AnalyzedFace(FaceObservation(0, 0, 80, 80, 0.9), FaceEmbedding((1.0, 0.0)))


class StubAnalyzer:
    def __init__(self, *faces: AnalyzedFace) -> None:
        self._faces = list(faces)

    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]:
        return self._faces


class FailingAnalyzer:
    def analyze(self, frame: np.ndarray) -> list[AnalyzedFace]:
        raise FaceAnalysisError("inference failed")


def _watchlist_with_one_reference(root: Path) -> Path:
    subject_dir = root / "moussa"
    subject_dir.mkdir()
    cv2.imwrite(str(subject_dir / "ref.png"), np.zeros((8, 8, 3), dtype=np.uint8))
    return root


def test_reliable_reference_is_loaded(tmp_path: Path) -> None:
    root = _watchlist_with_one_reference(tmp_path)
    watchlist = LocalWatchlistLoader(StubAnalyzer(_RELIABLE), _GATE).load(root)
    assert watchlist.size == 1


def test_too_far_reference_is_skipped(tmp_path: Path) -> None:
    root = _watchlist_with_one_reference(tmp_path)
    watchlist = LocalWatchlistLoader(StubAnalyzer(_TOO_FAR), _GATE).load(root)
    assert watchlist.size == 0


def test_analysis_failure_is_translated_to_watchlist_load_error(tmp_path: Path) -> None:
    root = _watchlist_with_one_reference(tmp_path)
    with pytest.raises(WatchlistLoadError):
        LocalWatchlistLoader(FailingAnalyzer(), _GATE).load(root)


def test_missing_root_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(WatchlistLoadError):
        LocalWatchlistLoader(StubAnalyzer(_RELIABLE), _GATE).load(tmp_path / "absent")
