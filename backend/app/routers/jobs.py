"""채용공고 엔드포인트."""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import job_repo
from app.schemas import JobListResponse, JobPostingRead, JobRefreshResponse
from app.services.work24_jobs import fetch_and_store, seed_sample

logger = logging.getLogger(__name__)
router = APIRouter()


def _auto_seed_if_empty(db: Session) -> None:
    if job_repo.count(db) == 0:
        logger.info("jobs table empty — auto-seeding sample data")
        seed_sample(db)


@router.get("", response_model=JobListResponse)
def list_jobs(
    q: str | None = Query(None, description="키워드 검색"),
    location: str | None = Query(None, description="지역 필터"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> JobListResponse:
    _auto_seed_if_empty(db)
    jobs = job_repo.list_jobs(db, q=q, location=location, limit=limit)
    return JobListResponse(
        jobs=[JobPostingRead.model_validate(j) for j in jobs],
        total=len(jobs),
        source="work24" if jobs and jobs[0].external_id.startswith("work24-") else "sample",
    )


@router.post("/refresh", response_model=JobRefreshResponse)
def refresh_jobs(db: Session = Depends(get_db)) -> JobRefreshResponse:
    """Work24 채용정보를 가져옵니다. 실패하면 샘플 데이터 fallback."""
    fetched, source = fetch_and_store(db)
    return JobRefreshResponse(fetched=fetched, source=source)


@router.post("/seed", response_model=JobRefreshResponse)
def seed_jobs(db: Session = Depends(get_db)) -> JobRefreshResponse:
    """샘플 채용공고를 시딩합니다."""
    fetched = seed_sample(db)
    return JobRefreshResponse(fetched=fetched, source="sample")
