"""add analysis history

Revision ID: 002_analysis_history
Revises: 001_initial_schema
"""
from alembic import op
import sqlalchemy as sa

revision = "002_analysis_history"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("analysis_history",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_type", sa.String(length=50), nullable=False),
        sa.Column("subject_id", sa.String(length=500), nullable=False),
        sa.Column("repository_name", sa.String(length=255)), sa.Column("branch_name", sa.String(length=255)),
        sa.Column("risk_score", sa.Integer(), nullable=False), sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False), sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False), sa.Column("summary", sa.Text()), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_analysis_history_subject_id", "analysis_history", ["subject_id"])
    op.create_index("ix_analysis_history_created_at", "analysis_history", ["created_at"])


def downgrade() -> None:
    op.drop_table("analysis_history")
