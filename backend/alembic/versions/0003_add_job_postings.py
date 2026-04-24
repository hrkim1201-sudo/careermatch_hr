"""add job_postings table

Revision ID: 0003_add_job_postings
Revises: 0002_add_qualifications
Create Date: 2026-04-24
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0003_add_job_postings"
down_revision: Union[str, None] = "0002_add_qualifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("external_id", sa.String(200), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("company", sa.String(300), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("salary", sa.String(200), nullable=True),
        sa.Column("employment_type", sa.String(100), nullable=True),
        sa.Column("deadline", sa.String(50), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("ncs_code", sa.String(50), nullable=True),
        sa.Column("ncs_name", sa.String(200), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_job_postings_external_id", "job_postings", ["external_id"], unique=True)
    op.create_index("ix_job_postings_title", "job_postings", ["title"])
    op.create_index("ix_job_postings_ncs_code", "job_postings", ["ncs_code"])


def downgrade() -> None:
    op.drop_index("ix_job_postings_ncs_code", table_name="job_postings")
    op.drop_index("ix_job_postings_title", table_name="job_postings")
    op.drop_index("ix_job_postings_external_id", table_name="job_postings")
    op.drop_table("job_postings")
