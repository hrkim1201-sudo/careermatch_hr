"""SQLAlchemy engine + session.

Railway PostgreSQL은 DATABASE_URL을 postgresql:// 형식으로 제공합니다.
SQLAlchemy 2.x는 postgresql+psycopg2:// 형식을 요구하므로 자동 변환합니다.
"""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _fix_database_url(url: str) -> str:
    """Railway가 주는 postgresql:// → postgresql+psycopg2:// 로 변환."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_settings = get_settings()
_db_url = _fix_database_url(_settings.database_url)

engine = create_engine(
    _db_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
