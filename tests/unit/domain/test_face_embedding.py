from __future__ import annotations

import pytest

from sentinel_vision.recognition.domain.face_embedding import FaceEmbedding


def test_identical_embeddings_have_similarity_of_one() -> None:
    embedding = FaceEmbedding((1.0, 2.0, 3.0))
    assert embedding.similarity_to(embedding) == pytest.approx(1.0)


def test_orthogonal_embeddings_have_similarity_of_zero() -> None:
    assert FaceEmbedding((1.0, 0.0)).similarity_to(FaceEmbedding((0.0, 1.0))) == pytest.approx(0.0)


def test_opposite_embeddings_have_similarity_of_minus_one() -> None:
    assert FaceEmbedding((1.0, 1.0)).similarity_to(FaceEmbedding((-1.0, -1.0))) == pytest.approx(-1.0)


def test_similarity_ignores_vector_magnitude() -> None:
    assert FaceEmbedding((1.0, 0.0)).similarity_to(FaceEmbedding((9.0, 0.0))) == pytest.approx(1.0)


def test_empty_embedding_is_rejected() -> None:
    with pytest.raises(ValueError):
        FaceEmbedding(())


def test_embedding_with_non_finite_values_is_rejected() -> None:
    for non_finite in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            FaceEmbedding((1.0, non_finite))


def test_comparing_different_dimensions_is_rejected() -> None:
    with pytest.raises(ValueError):
        FaceEmbedding((1.0, 2.0)).similarity_to(FaceEmbedding((1.0, 2.0, 3.0)))


def test_similarity_against_zero_norm_embedding_is_rejected() -> None:
    with pytest.raises(ValueError):
        FaceEmbedding((1.0, 1.0)).similarity_to(FaceEmbedding((0.0, 0.0)))
