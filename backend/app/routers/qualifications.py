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
        logger.info("qualifications empty — auto-seeding")
        seed_sample_qualifications(db)


@router.get("", response_model=QualificationListResponse)
def list_qualifications(
    q: str | None = Query(None),
    qual_type: str | None = Query(None),
    db: Session = Depends(get_db),
) -> QualificationListResponse:
    _auto_seed_if_empty(db)
    items = qualification_repo.list_qualifications(db, q=q, qual_type=qual_type)

    quals = [QualificationRead.model_validate(item) for item in items]

    # 각 자격의 다음 시험일정을 dict로 제공
    schedules: dict = {}
    for item in items:
        sched = qualification_repo.upcoming_schedule(db, item.qual_code)
        if sched:
            schedules[item.qual_code] = ExamScheduleRead.model_validate(sched).model_dump()

    return QualificationListResponse(
        qualifications=quals,
        schedules=schedules,
        total=len(quals),
    )


@router.post("/seed", response_model=QualRefreshResponse)
def seed_qualifications(db: Session = Depends(get_db)) -> QualRefreshResponse:
    fetched, schedules = seed_sample_qualifications(db)
    return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.post("/refresh", response_model=QualRefreshResponse)
def refresh_qualifications(db: Session = Depends(get_db)) -> QualRefreshResponse:
    try:
        fetched, schedules = qnet_qualifications.fetch_and_store(db)
        if fetched == 0:
            raise ValueError("empty")
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)
    except Exception as e:
        logger.warning("Q-Net failed: %s, fallback", e)
        fetched, schedules = seed_sample_qualifications(db)
        return QualRefreshResponse(fetched=fetched, schedules_fetched=schedules)


@router.get("/{qual_code}/schedules", response_model=list[ExamScheduleRead])
def get_schedules(qual_code: str, db: Session = Depends(get_db)):
    scheds = qualification_repo.list_schedules(db, qual_code=qual_code)
    return [ExamScheduleRead.model_validate(s) for s in scheds]


@router.get("/{qual_code}", response_model=QualificationRead)
def get_qualification(qual_code: str, db: Session = Depends(get_db)):
    item = qualification_repo.get_by_qual_code(db, qual_code)
    if item is None:
        raise NotFoundError(f"qualification {qual_code} not found")
    return QualificationRead.model_validate(item)
