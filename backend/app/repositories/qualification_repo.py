"""SQL access for NationalQualification and ExamSchedule."""
from collections.abc import Iterable, Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import ExamSchedule, NationalQualification


def list_qualifications(db: Session, q: str | None = None, qual_type: str | None = None) -> Sequence[NationalQualification]:
    stmt = select(NationalQualification)
    if q:
        stmt = stmt.where(
            NationalQualification.qual_name.ilike(f"%{q}%")
            | NationalQualification.job_field_name.ilike(f"%{q}%")
            | NationalQualification.mid_job_field.ilike(f"%{q}%")
        )
    if qual_type:
        stmt = stmt.where(NationalQualification.qual_type == qual_type)
    stmt = stmt.order_by(NationalQualification.qual_name)
    return db.execute(stmt).scalars().all()


def get_by_qual_code(db: Session, qual_code: str) -> NationalQualification | None:
    return db.execute(
        select(NationalQualification).where(NationalQualification.qual_code == qual_code)
    ).scalar_one_or_none()


def find_by_job_field(db: Session, job_field_code: str, limit: int = 10) -> Sequence[NationalQualification]:
    stmt = (
        select(NationalQualification)
        .where(NationalQualification.job_field_code == job_field_code)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def find_by_keywords(db: Session, keywords: list[str], limit: int = 5) -> Sequence[NationalQualification]:
    """Keyword match across qual_name, job_field_name, mid_job_field."""
    if not keywords:
        return []
    stmt = select(NationalQualification)
    conditions = []
    for kw in keywords:
        conditions.append(NationalQualification.qual_name.ilike(f"%{kw}%"))
        conditions.append(NationalQualification.job_field_name.ilike(f"%{kw}%"))
        conditions.append(NationalQualification.mid_job_field.ilike(f"%{kw}%"))
        conditions.append(NationalQualification.related_jobs.ilike(f"%{kw}%"))
    from sqlalchemy import or_
    stmt = stmt.where(or_(*conditions)).limit(limit)
    return db.execute(stmt).scalars().all()


def count_qualifications(db: Session) -> int:
    return db.execute(select(func.count(NationalQualification.id))).scalar_one()


def upsert_qualifications(db: Session, payloads: Iterable[dict]) -> int:
    payloads = list(payloads)
    if not payloads:
        return 0
    existing = {
        row[0]
        for row in db.execute(select(NationalQualification.qual_code)).all()
    }
    written = 0
    for p in payloads:
        code = p.get("qual_code")
        if not code:
            continue
        if code in existing:
            obj = get_by_qual_code(db, code)
            if obj:
                for k, v in p.items():
                    if k not in {"id", "created_at"}:
                        setattr(obj, k, v)
        else:
            db.add(NationalQualification(**p))
            existing.add(code)
        written += 1
    db.commit()
    return written


# ── ExamSchedule ────────────────────────────────────────────────────────────
def list_schedules(db: Session, qual_code: str | None = None) -> Sequence[ExamSchedule]:
    stmt = select(ExamSchedule).order_by(ExamSchedule.year.desc(), ExamSchedule.round_no)
    if qual_code:
        stmt = stmt.where(ExamSchedule.qual_code == qual_code)
    return db.execute(stmt).scalars().all()


def upcoming_schedule(db: Session, qual_code: str) -> ExamSchedule | None:
    """Return the earliest schedule that hasn't fully ended yet (by written_reg_start)."""
    stmt = (
        select(ExamSchedule)
        .where(ExamSchedule.qual_code == qual_code)
        .order_by(ExamSchedule.written_reg_start.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_schedules(db: Session, payloads: Iterable[dict]) -> int:
    payloads = list(payloads)
    if not payloads:
        return 0
    db.query(ExamSchedule).delete()
    for p in payloads:
        db.add(ExamSchedule(**p))
    db.commit()
    return len(payloads)
