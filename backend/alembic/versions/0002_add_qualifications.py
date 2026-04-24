"""add qualifications and exam schedules tables

Revision ID: 0002_add_qualifications
Revises: 0001_init
Create Date: 2026-04-22 00:00:00
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_qualifications"
down_revision: Union[str, None] = "0001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ncs_code / ncs_name 컬럼을 training_programs에 추가
    op.add_column("training_programs", sa.Column("ncs_code", sa.String(50), nullable=True))
    op.add_column("training_programs", sa.Column("ncs_name", sa.String(200), nullable=True))
    op.create_index("ix_training_programs_ncs_code", "training_programs", ["ncs_code"])

    op.create_table(
        "national_qualifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("qual_code", sa.String(20), nullable=False),
        sa.Column("qual_name", sa.String(200), nullable=False),
        sa.Column("qual_type", sa.String(30), nullable=True),
        sa.Column("job_field_code", sa.String(20), nullable=True),
        sa.Column("job_field_name", sa.String(100), nullable=True),
        sa.Column("mid_job_field", sa.String(100), nullable=True),
        sa.Column("related_jobs", sa.Text(), nullable=True),
        sa.Column("ministry", sa.String(100), nullable=True),
        sa.Column("written_fee", sa.String(50), nullable=True),
        sa.Column("practical_fee", sa.String(50), nullable=True),
        sa.Column("detail_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_national_qualifications_qual_code", "national_qualifications", ["qual_code"], unique=True)
    op.create_index("ix_national_qualifications_qual_name", "national_qualifications", ["qual_name"])
    op.create_index("ix_national_qualifications_qual_type", "national_qualifications", ["qual_type"])
    op.create_index("ix_national_qualifications_job_field_code", "national_qualifications", ["job_field_code"])

    op.create_table(
        "exam_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("qual_code", sa.String(20), nullable=False),
        sa.Column("qual_name", sa.String(200), nullable=False),
        sa.Column("year", sa.String(4), nullable=True),
        sa.Column("round_no", sa.String(10), nullable=True),
        sa.Column("written_reg_start", sa.String(20), nullable=True),
        sa.Column("written_reg_end", sa.String(20), nullable=True),
        sa.Column("written_exam_start", sa.String(20), nullable=True),
        sa.Column("written_exam_end", sa.String(20), nullable=True),
        sa.Column("written_result_date", sa.String(20), nullable=True),
        sa.Column("practical_reg_start", sa.String(20), nullable=True),
        sa.Column("practical_reg_end", sa.String(20), nullable=True),
        sa.Column("practical_exam_start", sa.String(20), nullable=True),
        sa.Column("practical_exam_end", sa.String(20), nullable=True),
        sa.Column("practical_result_date", sa.String(20), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="qnet"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_exam_schedules_qual_code", "exam_schedules", ["qual_code"])


def downgrade() -> None:
    op.drop_index("ix_exam_schedules_qual_code", table_name="exam_schedules")
    op.drop_table("exam_schedules")

    op.drop_index("ix_national_qualifications_job_field_code", table_name="national_qualifications")
    op.drop_index("ix_national_qualifications_qual_type", table_name="national_qualifications")
    op.drop_index("ix_national_qualifications_qual_name", table_name="national_qualifications")
    op.drop_index("ix_national_qualifications_qual_code", table_name="national_qualifications")
    op.drop_table("national_qualifications")

    op.drop_index("ix_training_programs_ncs_code", table_name="training_programs")
    op.drop_column("training_programs", "ncs_name")
    op.drop_column("training_programs", "ncs_code")
