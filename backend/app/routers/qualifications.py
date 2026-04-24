"""국가기술자격 엔드포인트."""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.repositories import qualification_repo
from app.schemas import (
    ExamScheduleRead,
    QualificationListResponse,
    QualificationRead,
    QualRefreshResponse,
)
from app.services import qnet_qualifications
from app.services.qualification_catalog import seed_sample_qualifications

logger = logging.getLogger(__name__)
router = APIRouter()


def _auto_seed_if_empty(db: Session) -> None:
    if qualification_repo.count_qualifications(db) == 0:
        logger.info("qualifications empty — auto-seeding sample data")
        seed_sample_qualifications(db)


@router.get("", response_model=QualificationListResponse)
def list_qualifications(
    q: str | None = Query(None),
    qual_type: str | None = Query(None),
    db: Session = Depends(get_db),
) -> QualificationListResponse:
    _auto_seed_if_empty(db)
    items = qualification_repo.list_qualifications(db, q=q, qual_type=qual_type)
    return QualificationListResponse(
        qualifications=[QualificationRead.model_validate(i) for i in items],
        total=len(items),
    )


@router.post("/seed", response_model=QualRefreshResponse)
def seed_qualifications(db: Session = Depends(get_db)) -> QualRefreshResponse:
    """샘플 자격 데이터를 시딩합니다. Q-Net API 없이 동작합니다."""
    fetched, schedules = seed_sample_qualifications(db)
    return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.post("/refresh", response_model=QualRefreshResponse)
def refresh_qualifications(db: Session = Depends(get_db)) -> QualRefreshResponse:
    """Q-Net에서 자격 데이터를 가져옵니다. 실패하면 샘플 데이터로 fallback합니다."""
    try:
        fetched, schedules = qnet_qualifications.fetch_and_store(db)
        if fetched == 0:
            raise ValueError("Q-Net returned 0 items")
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)
    except Exception as e:
        logger.warning("Q-Net fetch failed (%s), falling back to sample data", e)
        fetched, schedules = seed_sample_qualifications(db)
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.get("/{qual_code}/schedules", response_model=list[ExamScheduleRead])
def get_schedules(qual_code: str, db: Session = Depends(get_db)) -> list[ExamScheduleRead]:
    scheds = qualification_repo.list_schedules(db, qual_code=qual_code)
    return [ExamScheduleRead.model_validate(s) for s in scheds]


@router.get("/{qual_code}", response_model=QualificationRead)
def get_qualification(qual_code: str, db: Session = Depends(get_db)) -> QualificationRead:
    item = qualification_repo.get_by_qual_code(db, qual_code)
    if item is None:
        raise NotFoundError(f"qualification {qual_code} not found")
    return QualificationRead.model_validate(item)
