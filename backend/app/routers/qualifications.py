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


def _auto_seed_if_empty(db):
    if qualification_repo.count_qualifications(db) == 0:
        seed_sample_qualifications(db)


@router.get("", response_model=QualificationListResponse)
def list_qualifications(q=Query(None), qual_type=Query(None), db=Depends(get_db)):
    _auto_seed_if_empty(db)
    items = qualification_repo.list_qualifications(db, q=q, qual_type=qual_type)
    return QualificationListResponse(
        qualifications=[QualificationRead.model_validate(i) for i in items],
        total=len(items),
    )


@router.post("/seed", response_model=QualRefreshResponse)
def seed_qualifications(db=Depends(get_db)):
    fetched, schedules = seed_sample_qualifications(db)
    return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.post("/refresh", response_model=QualRefreshResponse)
def refresh_qualifications(db=Depends(get_db)):
    try:
        fetched, schedules = qnet_qualifications.fetch_and_store(db)
        if fetched == 0:
            raise ValueError("empty")
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)
    except Exception as e:
        logger.warning("Q-Net failed: %s", e)
        fetched, schedules = seed_sample_qualifications(db)
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.get("/{qual_code}/schedules", response_model=list[ExamScheduleRead])
def get_schedules(qual_code: str, db=Depends(get_db)):
    scheds = qualification_repo.list_schedules(db, qual_code=qual_code)
    return [ExamScheduleRead.model_validate(s) for s in scheds]


@router.get("/{qual_code}", response_model=QualificationRead)
def get_qualification(qual_code: str, db=Depends(get_db)):
    item = qualification_repo.get_by_qual_code(db, qual_code)
    if item is None:
        raise NotFoundError(f"qualification {qual_code} not found")
    return QualificationRead.model_validate(item)
