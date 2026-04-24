"""훈련과정 목록 및 시딩 엔드포인트.

고용24 API 접근이 제한되어 있으므로 샘플 데이터를 기본으로 사용합니다.
실제 훈련과정 데이터는 /api/programs/seed 엔드포인트로 시딩하거나
DB에 직접 입력하는 방식을 사용합니다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import program_repo
from app.schemas import ProgramListResponse, ProgramRead, ProgramRefreshResponse
from app.services import embedding
from app.services.program_catalog import seed_sample_programs

router = APIRouter()


@router.get("", response_model=ProgramListResponse)
def list_programs(db: Session = Depends(get_db)) -> ProgramListResponse:
    programs = program_repo.list_all(db)
    counts = program_repo.count_by_category(db)
    counts["total"] = sum(counts.values())
    source = programs[0].source if programs else "empty"
    return ProgramListResponse(
        programs=[ProgramRead.model_validate(p) for p in programs],
        counts=counts,
        source=source,
    )


@router.post("/seed", response_model=ProgramRefreshResponse)
def seed_programs(db: Session = Depends(get_db)) -> ProgramRefreshResponse:
    """샘플 훈련과정 데이터를 DB에 시딩합니다."""
    fetched = seed_sample_programs(db)
    embedding.reset_tfidf_cache()
    return ProgramRefreshResponse(fetched=fetched, source="sample")
