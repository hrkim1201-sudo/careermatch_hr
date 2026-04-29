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
        logger.info("jobs empty — auto-seeding")
        seed_sample(db)


@router.get("", response_model=JobListResponse)
def list_jobs(
    q: str | None = Query(None, description="키워드 검색"),
    location: str | None = Query(None, description="지역 필터"),
    ncs_code: str | None = Query(None, description="NCS 코드"),
    emp_type: str | None = Query(None, description="고용형태"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> JobListResponse:
    _auto_seed_if_empty(db)
    jobs = job_repo.list_jobs(db, q=q, location=location, ncs_code=ncs_code,
                               emp_type=emp_type, limit=limit, offset=offset)
    total = job_repo.count_jobs(db, q=q, location=location, ncs_code=ncs_code, emp_type=emp_type)
    return JobListResponse(
        jobs=[JobPostingRead.model_validate(j) for j in jobs],
        total=total,
        source="work24",
    )


@router.post("/refresh", response_model=JobRefreshResponse)
def refresh_jobs(db: Session = Depends(get_db)) -> JobRefreshResponse:
    fetched, source = fetch_and_store(db)
    return JobRefreshResponse(fetched=fetched, source=source)


@router.post("/seed", response_model=JobRefreshResponse)
def seed_jobs(db: Session = Depends(get_db)) -> JobRefreshResponse:
    fetched = seed_sample(db)
    return JobRefreshResponse(fetched=fetched, source="work24")


@router.delete("/all")
def delete_all_jobs(db: Session = Depends(get_db)):
    deleted = job_repo.delete_all(db)
    return {"deleted": deleted}
