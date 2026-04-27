"""Pydantic v2 schemas for API I/O."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Programs ────────────────────────────────────────────────────────────────
class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    provider: str | None = None
    program_type: str | None = None
    category: str | None = None
    location: str | None = None
    summary: str | None = None
    target_audience: str | None = None
    skills: str | None = None
    benefits: str | None = None
    schedule: str | None = None
    tuition: str | None = None
    url: str | None = None
    source: str
    external_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    ncs_code: str | None = None
    ncs_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ProgramListResponse(BaseModel):
    programs: list[ProgramRead]
    counts: dict[str, int]
    source: str


class ProgramRefreshResponse(BaseModel):
    fetched: int
    source: str


# ── National Qualifications ──────────────────────────────────────────────────
class QualificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    qual_code: str
    qual_name: str
    qual_type: str | None = None
    job_field_code: str | None = None
    job_field_name: str | None = None
    mid_job_field: str | None = None
    related_jobs: str | None = None
    ministry: str | None = None
    written_fee: str | None = None
    practical_fee: str | None = None
    detail_url: str | None = None
    created_at: datetime




class QualificationWithSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    qualification: QualificationRead
    next_exam: ExamScheduleRead | None = None

class QualificationListResponse(BaseModel):
    qualifications: list[QualificationRead]
    schedules: dict[str, "ExamScheduleRead"] = Field(default_factory=dict)
    total: int


class ExamScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    qual_code: str
    qual_name: str
    year: str | None = None
    round_no: str | None = None
    written_reg_start: str | None = None
    written_reg_end: str | None = None
    written_exam_start: str | None = None
    written_exam_end: str | None = None
    written_result_date: str | None = None
    practical_reg_start: str | None = None
    practical_reg_end: str | None = None
    practical_exam_start: str | None = None
    practical_exam_end: str | None = None
    practical_result_date: str | None = None
    source: str


class QualRefreshResponse(BaseModel):
    fetched: int
    schedules_fetched: int


# ── Portfolio ────────────────────────────────────────────────────────────────
class PortfolioCreate(BaseModel):
    prompt: str | None = None
    skills: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    prompt: str | None
    skills: list[str]
    preferences: dict[str, Any]
    created_at: datetime


# ── Match ────────────────────────────────────────────────────────────────────
class RelatedQualification(BaseModel):
    qualification: QualificationRead
    relevance: str          # "ncs_match" | "keyword" | "general"
    next_exam: ExamScheduleRead | None = None


class MatchItem(BaseModel):
    id: int
    program: ProgramRead
    score: float
    reason_keywords: list[str] = Field(default_factory=list)
    guide: str | None = None
    questions: list[str] = Field(default_factory=list)
    related_qualifications: list[RelatedQualification] = Field(default_factory=list)
    related_jobs: list["JobPostingRead"] = Field(default_factory=list)


class MatchRequest(BaseModel):
    prompt: str | None = None
    skills: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    top_k: int | None = None


class MatchResponse(BaseModel):
    results: list[MatchItem]
    used_method: str
    total_candidates: int


class GuideResponse(BaseModel):
    guide: str
    questions: list[str]
    used_method: str


# ── NLP Parser ───────────────────────────────────────────────────────────────
class ParseRequest(BaseModel):
    prompt: str


class ParsedInput(BaseModel):
    prompt: str
    skills: list[str] = Field(default_factory=list)
    location: str = ""
    online: bool = False
    parsed_by: str = "rule"


class DirectMatchRequest(BaseModel):
    """자연어 입력 → 파싱 → 추천을 한 번에."""
    prompt: str
    top_k: int | None = None


# ── Job Postings ─────────────────────────────────────────────────────────────
class JobPostingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str
    title: str
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    employment_type: str | None = None
    deadline: str | None = None
    summary: str | None = None
    skills: str | None = None
    url: str | None = None
    ncs_code: str | None = None
    ncs_name: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime


class JobListResponse(BaseModel):
    jobs: list[JobPostingRead]
    total: int
    source: str


class JobRefreshResponse(BaseModel):
    fetched: int
    source: str
