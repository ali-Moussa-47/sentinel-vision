from __future__ import annotations

from pathlib import Path

import cv2

from sentinel_vision.recognition.application.face_analyzer import FaceAnalysisError, FaceAnalyzer
from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.face_quality_gate import FaceQualityGate
from sentinel_vision.recognition.domain.watchlist import Watchlist, WatchlistSubject

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


class WatchlistLoadError(RuntimeError):
    pass


class LocalWatchlistLoader:
    def __init__(self, analyzer: FaceAnalyzer, quality_gate: FaceQualityGate) -> None:
        self._analyzer = analyzer
        self._quality_gate = quality_gate

    def load(self, root: Path) -> Watchlist:
        if not root.exists():
            raise WatchlistLoadError(f"watchlist path does not exist: {root}")

        subjects: list[WatchlistSubject] = []
        for subject_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            embeddings = self._load_subject_embeddings(subject_dir)
            if embeddings:
                subjects.append(
                    WatchlistSubject(
                        subject_dir.name,
                        _display_label(subject_dir.name),
                        tuple(embeddings),
                    )
                )
        return Watchlist(tuple(subjects))

    def _load_subject_embeddings(self, subject_dir: Path) -> list[FaceEmbedding]:
        embeddings: list[FaceEmbedding] = []
        for image_path in sorted(subject_dir.iterdir()):
            if image_path.suffix.lower() not in _IMAGE_SUFFIXES:
                continue
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            try:
                faces = self._analyzer.analyze(image)
            except FaceAnalysisError as error:
                raise WatchlistLoadError(f"could not analyze {image_path}: {error}") from error
            if len(faces) != 1:
                print(f"skipped reference {image_path.name}: expected exactly one face")
                continue
            if not self._quality_gate.is_reliable(faces[0].observation):
                print(f"skipped reference {image_path.name}: face too small or detection too weak")
                continue
            embeddings.append(faces[0].embedding)
        return embeddings


def _display_label(subject_id: str) -> str:
    return subject_id.replace("_", " ").strip()
