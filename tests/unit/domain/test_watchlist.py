from __future__ import annotations

import pytest

from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding
from sentinel_vision.recognition.domain.watchlist import Watchlist, WatchlistSubject


def _subject(subject_id: str, *references: FaceEmbedding) -> WatchlistSubject:
    return WatchlistSubject(subject_id, subject_id, references)


def test_subject_requires_at_least_one_reference_embedding() -> None:
    with pytest.raises(ValueError):
        WatchlistSubject("moussa", "Moussa", ())


def test_subject_similarity_uses_closest_reference() -> None:
    subject = _subject("moussa", FaceEmbedding((0.0, 1.0)), FaceEmbedding((1.0, 0.0)))
    assert subject.similarity_to(FaceEmbedding((1.0, 0.0))) == pytest.approx(1.0)


def test_empty_watchlist_has_no_best_match() -> None:
    assert Watchlist(()).best_match(FaceEmbedding((1.0, 0.0))) is None


def test_best_match_returns_closest_subject_label_and_score() -> None:
    watchlist = Watchlist((_subject("moussa", FaceEmbedding((1.0, 0.0))),))
    candidate = watchlist.best_match(FaceEmbedding((1.0, 0.0)))
    assert candidate is not None
    assert candidate.subject_label == "moussa"
    assert candidate.score == pytest.approx(1.0)


def test_best_match_picks_highest_scoring_subject() -> None:
    watchlist = Watchlist(
        (
            _subject("moussa", FaceEmbedding((1.0, 1.0))),
            _subject("awa", FaceEmbedding((1.0, 0.0))),
        )
    )
    candidate = watchlist.best_match(FaceEmbedding((1.0, 0.0)))
    assert candidate is not None
    assert candidate.subject_label == "awa"
