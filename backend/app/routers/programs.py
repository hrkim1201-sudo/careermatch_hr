"""훈련과정 엔드포인트."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import program_repo
from app.schemas import ProgramListResponse, ProgramRead, ProgramRefreshResponse
from app.services import embedding
from app.services.program_catalog import seed_sample_programs
from app.services.work24_programs import fetch_and_store

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


@router.post("/refresh", response_model=ProgramRefreshResponse)
def refresh_programs(db: Session = Depends(get_db)) -> ProgramRefreshResponse:
    """Work24 API에서 실데이터를 가져옵니다. 실패하면 샘플 데이터로 fallback."""
    fetched, source = fetch_and_store(db)
    embedding.reset_tfidf_cache()
    return ProgramRefreshResponse(fetched=fetched, source=source)


@router.post("/seed", response_model=ProgramRefreshResponse)
def seed_programs(db: Session = Depends(get_db)) -> ProgramRefreshResponse:
    """샘플 훈련과정 데이터를 시딩합니다."""
    fetched = seed_sample_programs(db)
    embedding.reset_tfidf_cache()
    return ProgramRefreshResponse(fetched=fetched, source="sample")
