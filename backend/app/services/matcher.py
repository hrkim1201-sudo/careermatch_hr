"""추천 엔진: 의미 기반 매칭 + 지역/온라인 필터링."""
from __future__ import annotations
import logging
import numpy as np
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models import TrainingProgram
from app.repositories import job_repo, program_repo
from app.schemas import JobPostingRead, MatchItem, MatchRequest, ProgramRead
from app.services import embedding
from app.services.nlp_parser import parse_prompt, build_query_text
from app.services.ncs_mapper import find_related_qualifications

logger = logging.getLogger(__name__)


def run_match(db: Session, req: MatchRequest) -> tuple[list[MatchItem], str, int]:
    settings = get_settings()
    programs = program_repo.list_all(db)
    if not programs:
        return [], "tfidf", 0

    # 1. 자연어 파싱
    parsed = parse_prompt(req.prompt or "")
    logger.info("parsed: %s", parsed)

    # 2. 쿼리 텍스트 구성 (원문 + 확장 키워드)
    query = build_query_text(req.prompt or "", parsed)

    # 3. 임베딩 & 코사인 유사도
    corpus = [_program_to_text(p) for p in programs]
    program_vectors, _ = embedding.embed_corpus(corpus)
    query_vector, used_method = embedding.embed_query(query, corpus_for_fallback=corpus)
    scores = _cosine_sim(query_vector, program_vectors)

    # 4. 지역 필터 보너스
    region = parsed.get("region")
    online = parsed.get("online", False)
    for i, p in enumerate(programs):
        loc = (p.location or "").lower()
        if region and region in (p.location or ""):
            scores[i] = min(1.0, scores[i] * 1.25)  # 지역 일치 25% 보너스
        if online and ("온라인" in loc or "비대면" in loc or "원격" in loc):
            scores[i] = min(1.0, scores[i] * 1.20)  # 온라인 20% 보너스

    # 5. 상위 K개
    top_k = req.top_k or settings.match_top_k
    ranked_idx = np.argsort(-scores)[:top_k * 2]  # 후보 더 뽑고

    # 6. 최소 점수 필터 & 결과 구성
    query_keywords = (parsed.get("expanded_keywords") or parsed.get("job_keywords") or [])[:8]

    items: list[MatchItem] = []
    for idx in ranked_idx:
        if len(items) >= top_k:
            break
        score = float(scores[int(idx)])
        if score < 0.0:
            continue
        program = programs[int(idx)]
        related_quals = find_related_qualifications(db, program, query_keywords, top_k=settings.qual_top_k)
        related_jobs = _find_related_jobs(db, program, query_keywords)
        reason_kws = _pick_reason_keywords(query_keywords, program)

        items.append(MatchItem(
            id=program.id,
            program=ProgramRead.model_validate(program),
            score=round(score * 100, 2),
            reason_keywords=reason_kws,
            related_qualifications=related_quals,
            related_jobs=related_jobs,
        ))

    logger.info("match: method=%s candidates=%d returned=%d", used_method, len(programs), len(items))
    return items, used_method, len(programs)


def _find_related_jobs(db, program: TrainingProgram, query_keywords: list[str]) -> list[JobPostingRead]:
    keywords = []
    if program.ncs_name:
        keywords.append(program.ncs_name)
    if program.skills:
        keywords.extend(program.skills.split()[:3])
    keywords.extend(query_keywords[:3])
    keywords = list(dict.fromkeys(keywords))[:6]
    jobs = job_repo.find_by_keywords(db, keywords, limit=3)
    return [JobPostingRead.model_validate(j) for j in jobs]


def _program_to_text(p: TrainingProgram) -> str:
    """프로그램을 임베딩용 텍스트로 변환 - 핵심 정보 강조."""
    parts = []
    if p.title:
        parts.append(p.title)
        parts.append(p.title)  # 제목 가중치 2배
    if p.summary:
        parts.append(p.summary)
    if p.skills:
        parts.append(p.skills)
        parts.append(p.skills)  # 스킬 가중치 2배
    if p.target_audience:
        parts.append(p.target_audience)
    if p.ncs_name:
        parts.append(p.ncs_name)
    if p.tags:
        parts.append(" ".join(p.tags))
    if p.category:
        parts.append(p.category)
    if p.location:
        parts.append(p.location)
    return " ".join(parts).strip()


def _cosine_sim(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    q_norm = np.linalg.norm(query) + 1e-12
    m_norms = np.linalg.norm(matrix, axis=1) + 1e-12
    return matrix @ query / (m_norms * q_norm)


def _pick_reason_keywords(query_keywords: list[str], program: TrainingProgram, k: int = 4) -> list[str]:
    pool = list(program.tags or [])
    if program.skills:
        pool.extend(program.skills.split()[:6])
    if program.ncs_name:
        pool.append(program.ncs_name)

    seen: set[str] = set()
    out: list[str] = []
    qk_lower = {q.lower() for q in query_keywords}

    for word in pool:
        key = word.lower()
        if key in seen:
            continue
        seen.add(key)
        if any(q in key or key in q for q in qk_lower):
            out.append(word)
        if len(out) >= k:
            break

    return out or (program.tags or [])[:k]
