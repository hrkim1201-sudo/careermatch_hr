"""Single point of contact for `TrainingProgram` SQL.

Routers and services must NOT touch `db.query(TrainingProgram)` directly;
they call functions defined here. This makes it trivial to swap the
storage engine (e.g. add caching, switch to async) without touching
business logic.
"""
from collections.abc import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import CompileError
from sqlalchemy.orm import Session

from app.models import TrainingProgram


def list_all(db: Session) -> Sequence[TrainingProgram]:
    return db.execute(select(TrainingProgram).order_by(TrainingProgram.id.desc())).scalars().all()


def get_by_id(db: Session, program_id: int) -> TrainingProgram | None:
    return db.get(TrainingProgram, program_id)


def get_by_external_id(db: Session, external_id: str) -> TrainingProgram | None:
    stmt = select(TrainingProgram).where(TrainingProgram.external_id == external_id)
    return db.execute(stmt).scalar_one_or_none()


def count(db: Session) -> int:
    return db.execute(select(func.count(TrainingProgram.id))).scalar_one()


def count_by_category(db: Session) -> dict[str, int]:
    stmt = select(TrainingProgram.category, func.count(TrainingProgram.id)).group_by(
        TrainingProgram.category
    )
    rows = db.execute(stmt).all()
    return {(category or "기타"): n for category, n in rows}


def upsert_many(db: Session, payloads: Iterable[dict]) -> int:
    """Insert or update rows by `external_id`.

    Uses Postgres ON CONFLICT when available; otherwise falls back to
    a portable SELECT-then-INSERT/UPDATE loop (so the test suite can
    run on SQLite).
    """
    payloads = list(payloads)
    if not payloads:
        return 0

    try:
        stmt = pg_insert(TrainingProgram).values(payloads)
        update_cols = {
            col.name: col
            for col in stmt.excluded
            if col.name not in {"id", "created_at", "external_id"}
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=[TrainingProgram.external_id],
            set_=update_cols,
        )
        db.execute(stmt)
        db.commit()
        return len(payloads)
    except (CompileError, NotImplementedError):
        # SQLite fallback for tests
        return _upsert_portable(db, payloads)


def _upsert_portable(db: Session, payloads: list[dict]) -> int:
    written = 0
    for payload in payloads:
        external_id = payload.get("external_id")
        existing = get_by_external_id(db, external_id) if external_id else None
        if existing is None:
            db.add(TrainingProgram(**payload))
            written += 1
        else:
            for k, v in payload.items():
                if k in {"id", "created_at"}:
                    continue
                setattr(existing, k, v)
            written += 1
    db.commit()
    return written


def delete_all(db: Session) -> int:
    deleted = db.query(TrainingProgram).delete()
    db.commit()
    return deleted
