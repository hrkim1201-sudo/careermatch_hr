"""Embedding service unit tests."""
from __future__ import annotations

import numpy as np

from app.services import embedding


def test_tfidf_query_is_deterministic() -> None:
    embedding.reset_tfidf_cache()
    corpus = ["python fastapi backend", "react frontend ui", "data analysis sql"]
    v1, m1 = embedding.embed_query("python", corpus)
    v2, m2 = embedding.embed_query("python", corpus)
    assert m1 == "tfidf" and m2 == "tfidf"
    np.testing.assert_array_equal(v1, v2)


def test_tfidf_query_dimension_matches_corpus_vocabulary() -> None:
    embedding.reset_tfidf_cache()
    corpus = ["python fastapi backend", "react frontend ui"]
    q_vec, _ = embedding.embed_query("python", corpus)
    c_matrix, _ = embedding.embed_corpus(corpus)
    assert q_vec.shape[0] == c_matrix.shape[1]


def test_tfidf_handles_empty_text() -> None:
    embedding.reset_tfidf_cache()
    corpus = ["python", "react"]
    vec, method = embedding.embed_query("", corpus)
    assert method == "tfidf"
    assert vec.shape[0] > 0
