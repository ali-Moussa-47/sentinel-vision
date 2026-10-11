from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from sentinel_vision.recognition.domain.recognition_result import Decision, RecognitionResult


@dataclass(frozen=True)
class MatchConfirmation:
    confirm_frames: int

    def confirm(self, history: Sequence[RecognitionResult]) -> RecognitionResult:
        if not history:
            return RecognitionResult.unknown(0.0)
        latest = history[-1]
        label = latest.subject_label
        if latest.decision is Decision.POTENTIAL_MATCH and label is not None:
            matches = [
                result
                for result in history
                if result.decision is Decision.POTENTIAL_MATCH and result.subject_label == label
            ]
            if len(matches) >= self.confirm_frames:
                return RecognitionResult.potential_match(label, max(m.score for m in matches))
            return RecognitionResult.unknown(latest.score)
        if latest.decision is Decision.INSUFFICIENT_QUALITY:
            return RecognitionResult.insufficient_quality()
        return RecognitionResult.unknown(latest.score)
