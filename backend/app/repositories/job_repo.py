"""SQL access for JobPosting."""
from collections.abc import Iterable, Sequence
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.models import JobPosting


def list_jobs(db: Session, q: str | None = None, location: str | None = None,
              ncs_code: str | None = None, emp_type: str | None = None,
              limit: int = 50, offset: int = 0) -> Sequence[JobPosting]:
    stmt = select(JobPosting).order_by(JobPosting.id.desc())
    if q:
        stmt = stmt.where(or_(
            JobPosting.title.ilike(f"%{q}%"),
            JobPosting.company.ilike(f"%{q}%"),
            JobPosting.skills.ilike(f"%{q}%"),
            JobPosting.ncs_name.ilike(f"%{q}%"),
            JobPosting.summary.ilike(f"%{q}%"),
        ))
    if location:
        stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
    if ncs_code:
        stmt = stmt.where(JobPosting.ncs_code == ncs_code)
    if emp_type:
        stmt = stmt.where(JobPosting.employment_type == emp_type)
    stmt = stmt.offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def count_jobs(db: Session, q: str | None = None, location: str | None = None,
               ncs_code: str | None = None, emp_type: str | None = None) -> int:
    stmt = select(func.count(JobPosting.id))
    if q:
        stmt = stmt.where(or_(
            JobPosting.title.ilike(f"%{q}%"),
            JobPosting.company.ilike(f"%{q}%"),
            JobPosting.skills.ilike(f"%{q}%"),
            JobPosting.ncs_name.ilike(f"%{q}%"),
        ))
    if location:
        stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
    if ncs_code:
        stmt = stmt.where(JobPosting.ncs_code == ncs_code)
    if emp_type:
        stmt = stmt.where(JobPosting.employment_type == emp_type)
    return db.execute(stmt).scalar_one()


def find_by_keywords(db: Session, keywords: list[str], limit: int = 5) -> Sequence[JobPosting]:
    if not keywords:
        return []
    conditions = []
    for kw in keywords:
        conditions.extend([
            JobPosting.title.ilike(f"%{kw}%"),
            JobPosting.skills.ilike(f"%{kw}%"),
            JobPosting.ncs_name.ilike(f"%{kw}%"),
            JobPosting.summary.ilike(f"%{kw}%"),
        ])
    stmt = select(JobPosting).where(or_(*conditions)).order_by(JobPosting.id.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def count(db: Session) -> int:
    return db.execute(select(func.count(JobPosting.id))).scalar_one()


def upsert_many(db: Session, payloads: Iterable[dict]) -> int:
    payloads = list(payloads)
    if not payloads:
        return 0
    # 배치 처리 (4400개 효율화)
    existing = set()
    for row in db.execute(select(JobPosting.external_id)).all():
        existing.add(row[0])
    written = 0
    batch = []
    for p in payloads:
        eid = p.get("external_id")
        if not eid:
            continue
        if eid not in existing:
            batch.append(JobPosting(**p))
            existing.add(eid)
            written += 1
        if len(batch) >= 500:
            db.bulk_save_objects(batch)
            db.flush()
            batch = []
    if batch:
        db.bulk_save_objects(batch)
    db.commit()
    return written


def delete_all(db: Session) -> int:
    deleted = db.query(JobPosting).delete()
    db.commit()
    return deleted
