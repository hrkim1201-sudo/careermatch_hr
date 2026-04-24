"""SQL access for JobPosting."""
from collections.abc import Iterable, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import JobPosting


def list_jobs(
    db: Session,
    q: str | None = None,
    location: str | None = None,
    limit: int = 50,
) -> Sequence[JobPosting]:
    stmt = select(JobPosting).order_by(JobPosting.id.desc())
    if q:
        stmt = stmt.where(
            or_(
                JobPosting.title.ilike(f"%{q}%"),
                JobPosting.company.ilike(f"%{q}%"),
                JobPosting.skills.ilike(f"%{q}%"),
                JobPosting.ncs_name.ilike(f"%{q}%"),
            )
        )
    if location:
        stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()


def find_by_keywords(
    db: Session, keywords: list[str], limit: int = 5
) -> Sequence[JobPosting]:
    if not keywords:
        return []
    conditions = []
    for kw in keywords:
        conditions.append(JobPosting.title.ilike(f"%{kw}%"))
        conditions.append(JobPosting.skills.ilike(f"%{kw}%"))
        conditions.append(JobPosting.ncs_name.ilike(f"%{kw}%"))
        conditions.append(JobPosting.summary.ilike(f"%{kw}%"))
    stmt = (
        select(JobPosting)
        .where(or_(*conditions))
        .order_by(JobPosting.id.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def count(db: Session) -> int:
    return db.execute(select(func.count(JobPosting.id))).scalar_one()


def upsert_many(db: Session, payloads: Iterable[dict]) -> int:
    payloads = list(payloads)
    if not payloads:
        return 0
    existing = {
        row[0]
        for row in db.execute(select(JobPosting.external_id)).all()
    }
    written = 0
    for p in payloads:
        eid = p.get("external_id")
        if not eid:
            continue
        if eid not in existing:
            db.add(JobPosting(**p))
            existing.add(eid)
        else:
            obj = db.execute(
                select(JobPosting).where(JobPosting.external_id == eid)
            ).scalar_one_or_none()
            if obj:
                for k, v in p.items():
                    if k not in {"id", "created_at"}:
                        setattr(obj, k, v)
        written += 1
    db.commit()
    return written


def delete_all(db: Session) -> int:
    deleted = db.query(JobPosting).delete()
    db.commit()
    return deleted
