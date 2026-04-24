"""Text embedding with graceful degradation.

Strategy:
  1. If `OPENAI_API_KEY` is set, call OpenAI embeddings.
  2. On any failure (network, rate limit, missing key), fall back to TF-IDF.
  3. Caller is told which path was used so the UI can surface this fact.

The TF-IDF vectorizer is fit on the supplied corpus on first use and
cached process-wide. If the corpus changes (new programs are added),
call `reset_tfidf_cache()`.
"""
from __future__ import annotations

import logging
import threading
from collections.abc import Sequence
from typing import Literal

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import get_settings

logger = logging.getLogger(__name__)

EmbedMethod = Literal["openai", "tfidf"]

_tfidf_lock = threading.Lock()
_tfidf_vectorizer: TfidfVectorizer | None = None
_tfidf_corpus_signature: int | None = None


def reset_tfidf_cache() -> None:
    global _tfidf_vectorizer, _tfidf_corpus_signature
    with _tfidf_lock:
        _tfidf_vectorizer = None
        _tfidf_corpus_signature = None


def embed_query(
    text: str, corpus_for_fallback: Sequence[str]
) -> tuple[np.ndarray, EmbedMethod]:
    """Embed `text`. Returns (vector, method)."""
    settings = get_settings()
    text = (text or "").strip() or " "

    if settings.openai_api_key:
        try:
            vec = _openai_embed(text)
            return np.asarray(vec, dtype=np.float32), "openai"
        except Exception as e:
            logger.warning("openai embed failed; falling back to tfidf: %s", e)

    vec = _tfidf_embed_query(text, corpus_for_fallback)
    return vec, "tfidf"


def embed_corpus(
    corpus: Sequence[str],
) -> tuple[np.ndarray, EmbedMethod]:
    """Embed all corpus documents. Returns (matrix, method).

    Always uses the same method as `embed_query` would for consistency
    of the similarity space.
    """
    settings = get_settings()
    corpus = [c if c and c.strip() else " " for c in corpus]

    if settings.openai_api_key:
        try:
            vecs = _openai_embed_batch(corpus)
            return np.asarray(vecs, dtype=np.float32), "openai"
        except Exception as e:
            logger.warning("openai batch embed failed; falling back to tfidf: %s", e)

    matrix = _tfidf_embed_corpus(corpus)
    return matrix, "tfidf"


# --------------------------------------------------------------------------- #
# OpenAI path
# --------------------------------------------------------------------------- #
def _openai_embed(text: str) -> list[float]:
    settings = get_settings()
    # Lazy import so test environments without `openai` installed still work.
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_request_timeout)
    res = client.embeddings.create(model=settings.openai_embedding_model, input=text)
    return res.data[0].embedding


def _openai_embed_batch(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_request_timeout)
    res = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [d.embedding for d in res.data]


# --------------------------------------------------------------------------- #
# TF-IDF path
# --------------------------------------------------------------------------- #
def _ensure_tfidf(corpus: Sequence[str]) -> TfidfVectorizer:
    global _tfidf_vectorizer, _tfidf_corpus_signature

    sig = hash(tuple(corpus))
    with _tfidf_lock:
        if _tfidf_vectorizer is None or _tfidf_corpus_signature != sig:
            vec = TfidfVectorizer(
                max_features=4000,
                ngram_range=(1, 2),
                sublinear_tf=True,
            )
            vec.fit(list(corpus) or [" "])
            _tfidf_vectorizer = vec
            _tfidf_corpus_signature = sig
        return _tfidf_vectorizer


def _tfidf_embed_query(text: str, corpus: Sequence[str]) -> np.ndarray:
    vec = _ensure_tfidf(corpus)
    return vec.transform([text]).toarray()[0].astype(np.float32)


def _tfidf_embed_corpus(corpus: Sequence[str]) -> np.ndarray:
    vec = _ensure_tfidf(corpus)
    return vec.transform(list(corpus)).toarray().astype(np.float32)
