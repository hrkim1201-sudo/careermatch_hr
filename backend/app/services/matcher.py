"""추천 엔진: 훈련과정 점수 계산 + 연관 국가자격 연계."""
from __future__ import annotations

import logging
from collections.abc import Sequence

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import TrainingProgram
from app.repositories import program_repo
from app.schemas import MatchItem, MatchRequest, ProgramRead
from app.services import embedding
from app.services.ncs_mapper import find_related_qualifications

logger = logging.getLogger(__name__)


def run_match(db: Session, req: MatchRequest) -> tuple[list[MatchItem], str, int]:
    settings = get_settings()
    programs = program_repo.list_all(db)
    if not programs:
        return [], "tfidf", 0

    corpus = [_program_to_text(p) for p in programs]
    query = _build_query_text(req)

    program_vectors, _ = embedding.embed_corpus(corpus)
    query_vector, used_method = embedding.embed_query(query, corpus_for_fallback=corpus)
    scores = _cosine_sim(query_vector, program_vectors)

    top_k = req.top_k or settings.match_top_k
    ranked_idx = np.argsort(-scores)[:top_k]
    query_keywords = [t.strip() for t in query.split() if len(t.strip()) > 1][:8]

    items: list[MatchItem] = []
    for idx in ranked_idx:
        score = float(scores[int(idx)])
        if score < settings.match_min_score:
            continue
        program = programs[int(idx)]
        related_quals = find_related_qualifications(
            db, program, query_keywords, top_k=settings.qual_top_k
        )
        items.append(
            MatchItem(
                id=program.id,
                program=ProgramRead.model_validate(program),
                score=round(score * 100, 2),
                reason_keywords=_pick_reason_keywords(query, program),
                related_qualifications=related_quals,
            )
        )

    logger.info(
        "match completed",
        extra={"ctx": {"method": used_method, "candidates": len(programs), "returned": len(items)}},
    )
    return items, used_method, len(programs)


def _program_to_text(p: TrainingProgram) -> str:
    parts = [
        p.title or "", p.summary or "", p.skills or "",
        p.target_audience or "", " ".join(p.tags or []),
        p.category or "", p.ncs_name or "",
    ]
    return " ".join(parts).strip()


def _build_query_text(req: MatchRequest) -> str:
    bits: list[str] = []
    if req.prompt:
        bits.append(req.prompt)
    if req.skills:
        bits.append(" ".join(req.skills))
    if req.preferences:
        for v in req.preferences.values():
            if isinstance(v, str) and v:
                bits.append(v)
            elif isinstance(v, list):
                bits.append(" ".join(str(x) for x in v))
    return " ".join(bits).strip() or "취업 준비"


def _cosine_sim(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    q_norm = np.linalg.norm(query) + 1e-12
    m_norms = np.linalg.norm(matrix, axis=1) + 1e-12
    return matrix @ query / (m_norms * q_norm)


def _pick_reason_keywords(query: str, program: TrainingProgram, k: int = 4) -> list[str]:
    tokens = {t.lower() for t in query.replace(",", " ").split() if len(t) > 1}
    pool = list(program.tags or [])
    if program.skills:
        pool.extend(program.skills.split())
    seen: set[str] = set()
    out: list[str] = []
    for word in pool:
        key = word.lower()
        if key in seen:
            continue
        seen.add(key)
        if any(t in key or key in t for t in tokens):
            out.append(word)
        if len(out) >= k:
            break
    return out or (program.tags or [])[:k]
