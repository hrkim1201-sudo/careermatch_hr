"""ORM models.

TrainingProgram: 고용24 국민내일배움카드 훈련과정
NationalQualification: Q-Net 국가기술자격 종목
ExamSchedule: 자격 시험 회차별 일정
Portfolio, MatchResult: 사용자 입력 및 추천 이력
"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    provider: Mapped[str | None] = mapped_column(String(300))
    program_type: Mapped[str | None] = mapped_column(String(50), index=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    location: Mapped[str | None] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text)
    target_audience: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)
    benefits: Mapped[str | None] = mapped_column(Text)
    schedule: Mapped[str | None] = mapped_column(String(300))
    tuition: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), default="sample", index=True)
    external_id: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    # NCS 연계 코드 (대분류.중분류.소분류.세분류)
    ncs_code: Mapped[str | None] = mapped_column(String(50), index=True)
    ncs_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class NationalQualification(Base):
    """Q-Net 국가기술자격 종목 정보."""
    __tablename__ = "national_qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Q-Net 자격코드 (예: 1320)
    qual_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    qual_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    # 자격구분: 기술사/기능장/기사/산업기사/기능사
    qual_type: Mapped[str | None] = mapped_column(String(30), index=True)
    # 직무분야 (NCS 분류 연계)
    job_field_code: Mapped[str | None] = mapped_column(String(20), index=True)
    job_field_name: Mapped[str | None] = mapped_column(String(100))
    # 중직무분야
    mid_job_field: Mapped[str | None] = mapped_column(String(100))
    # 관련 직업 / 취득 후 진출 분야
    related_jobs: Mapped[str | None] = mapped_column(Text)
    # 주관 부처
    ministry: Mapped[str | None] = mapped_column(String(100))
    # 수수료
    written_fee: Mapped[str | None] = mapped_column(String(50))
    practical_fee: Mapped[str | None] = mapped_column(String(50))
    # Q-Net 상세 URL
    detail_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ExamSchedule(Base):
    """국가기술자격 시험 회차별 일정."""
    __tablename__ = "exam_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qual_code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    qual_name: Mapped[str] = mapped_column(String(200), nullable=False)
    year: Mapped[str | None] = mapped_column(String(4))
    round_no: Mapped[str | None] = mapped_column(String(10))  # 회차
    # 필기
    written_reg_start: Mapped[str | None] = mapped_column(String(20))
    written_reg_end: Mapped[str | None] = mapped_column(String(20))
    written_exam_start: Mapped[str | None] = mapped_column(String(20))
    written_exam_end: Mapped[str | None] = mapped_column(String(20))
    written_result_date: Mapped[str | None] = mapped_column(String(20))
    # 실기
    practical_reg_start: Mapped[str | None] = mapped_column(String(20))
    practical_reg_end: Mapped[str | None] = mapped_column(String(20))
    practical_exam_start: Mapped[str | None] = mapped_column(String(20))
    practical_exam_end: Mapped[str | None] = mapped_column(String(20))
    practical_result_date: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(20), default="qnet")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prompt: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list | None] = mapped_column(JSON, default=list)
    preferences: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int | None] = mapped_column(Integer, index=True)
    program_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    used_method: Mapped[str] = mapped_column(String(20), nullable=False)
    guide: Mapped[str | None] = mapped_column(Text)
    questions: Mapped[list | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class JobPosting(Base):
    """Work24 채용공고."""
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(300))
    location: Mapped[str | None] = mapped_column(String(200))
    salary: Mapped[str | None] = mapped_column(String(200))
    employment_type: Mapped[str | None] = mapped_column(String(100))
    deadline: Mapped[str | None] = mapped_column(String(50))
    summary: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    ncs_code: Mapped[str | None] = mapped_column(String(50), index=True)
    ncs_name: Mapped[str | None] = mapped_column(String(200))
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
