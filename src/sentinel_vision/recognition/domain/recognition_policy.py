from __future__ import annotations

from dataclasses import dataclass

from sentinel_vision.recognition.domain.recognition_result import RecognitionResult
from sentinel_vision.recognition.domain.watchlist import Candidate


@dataclass(frozen=True)
class RecognitionPolicy:
    match_threshold: float

    def decide(self, candidate: Candidate | None) -> RecognitionResult:
        if candidate is None:
            return RecognitionResult.unknown(0.0)
        if candidate.score >= self.match_threshold:
            return RecognitionResult.potential_match(candidate.subject_label, candidate.score)
        return RecognitionResult.unknown(candidate.score)
