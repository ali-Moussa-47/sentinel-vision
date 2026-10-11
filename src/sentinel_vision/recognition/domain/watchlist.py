from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding


@dataclass(frozen=True)
class Candidate:
    subject_label: str
    score: float


@dataclass(frozen=True)
class WatchlistSubject:
    subject_id: str
    display_label: str
    reference_embeddings: tuple[FaceEmbedding, ...]

    def __post_init__(self) -> None:
        if not self.reference_embeddings:
            raise ValueError(f"subject {self.subject_id!r} has no reference embeddings")

    def similarity_to(self, probe: FaceEmbedding) -> float:
        return max(reference.similarity_to(probe) for reference in self.reference_embeddings)


@dataclass(frozen=True)
class Watchlist:
    subjects: tuple[WatchlistSubject, ...]

    @property
    def size(self) -> int:
        return len(self.subjects)

    def best_match(self, probe: FaceEmbedding) -> Candidate | None:
        if not self.subjects:
            return None
        subject, score = max(
            ((subject, subject.similarity_to(probe)) for subject in self.subjects),
            key=lambda scored: scored[1],
        )
        return Candidate(subject.display_label, score)
