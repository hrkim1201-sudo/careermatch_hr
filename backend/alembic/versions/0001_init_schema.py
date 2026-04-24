"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-04-21 00:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "training_programs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("provider", sa.String(length=300), nullable=True),
        sa.Column("program_type", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("schedule", sa.String(length=300), nullable=True),
        sa.Column("tuition", sa.String(length=200), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="sample"),
        sa.Column("external_id", sa.String(length=200), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_training_programs_title", "training_programs", ["title"])
    op.create_index("ix_training_programs_program_type", "training_programs", ["program_type"])
    op.create_index("ix_training_programs_category", "training_programs", ["category"])
    op.create_index("ix_training_programs_source", "training_programs", ["source"])
    op.create_index("ix_training_programs_external_id", "training_programs", ["external_id"], unique=True)

    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "match_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("portfolio_id", sa.Integer(), nullable=True),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("used_method", sa.String(length=20), nullable=False),
        sa.Column("guide", sa.Text(), nullable=True),
        sa.Column("questions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_match_results_portfolio_id", "match_results", ["portfolio_id"])
    op.create_index("ix_match_results_program_id", "match_results", ["program_id"])


def downgrade() -> None:
    op.drop_index("ix_match_results_program_id", table_name="match_results")
    op.drop_index("ix_match_results_portfolio_id", table_name="match_results")
    op.drop_table("match_results")

    op.drop_table("portfolios")

    op.drop_index("ix_training_programs_external_id", table_name="training_programs")
    op.drop_index("ix_training_programs_source", table_name="training_programs")
    op.drop_index("ix_training_programs_category", table_name="training_programs")
    op.drop_index("ix_training_programs_program_type", table_name="training_programs")
    op.drop_index("ix_training_programs_title", table_name="training_programs")
    op.drop_table("training_programs")
