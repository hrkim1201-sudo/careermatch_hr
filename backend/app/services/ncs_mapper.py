"""NCS 코드 기반 훈련과정 ↔ 국가자격 연계.

NCS(국가직무능력표준) 코드 체계:
  대분류(2자리).중분류(2자리).소분류(2자리).세분류(2자리)
  예) 09.02.01.02 = 전기전자 > 전자기기개발 > 전자제품개발 > 디지털회로개발

훈련과정의 ncs_code와 자격종목의 job_field_code를 대분류 수준에서 매칭합니다.
코드가 없는 경우 키워드 기반 매칭으로 fallback합니다.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models import ExamSchedule, NationalQualification, TrainingProgram
from app.repositories import qualification_repo
from app.schemas import ExamScheduleRead, QualificationRead, RelatedQualification

logger = logging.getLogger(__name__)


def find_related_qualifications(
    db: Session,
    program: TrainingProgram,
    query_keywords: list[str],
    top_k: int = 5,
) -> list[RelatedQualification]:
    """훈련과정 1개에 대해 연관 국가자격 목록을 반환."""
    found: list[tuple[NationalQualification, str]] = []  # (qual, relevance_type)
    seen: set[str] = set()

    # 1순위: NCS 코드 매칭
    if program.ncs_code:
        ncs_major = program.ncs_code.split(".")[0]
        by_ncs = qualification_repo.find_by_job_field(db, ncs_major, limit=top_k)
        for q in by_ncs:
            if q.qual_code not in seen:
                found.append((q, "ncs_match"))
                seen.add(q.qual_code)

    # 2순위: 훈련 제목 + NCS명 + 스킬 키워드로 검색
    if len(found) < top_k:
        kws = _extract_keywords(program) + query_keywords
        kws = list(dict.fromkeys(kws))[:6]
        by_kw = qualification_repo.find_by_keywords(db, kws, limit=top_k - len(found))
        for q in by_kw:
            if q.qual_code not in seen:
                found.append((q, "keyword"))
                seen.add(q.qual_code)

    results: list[RelatedQualification] = []
    for qual, relevance in found[:top_k]:
        next_sched = qualification_repo.upcoming_schedule(db, qual.qual_code)
        results.append(
            RelatedQualification(
                qualification=QualificationRead.model_validate(qual),
                relevance=relevance,
                next_exam=ExamScheduleRead.model_validate(next_sched) if next_sched else None,
            )
        )
    return results


def _extract_keywords(program: TrainingProgram) -> list[str]:
    tokens: list[str] = []
    for field in [program.ncs_name, program.title, program.skills]:
        if field:
            tokens.extend(t.strip() for t in field.replace(",", " ").split() if len(t.strip()) > 1)
    return list(dict.fromkeys(tokens))[:8]
