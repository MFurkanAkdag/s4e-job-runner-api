#app/db/migrations/version/20250812_0001_init.py

"""initial schema: job_runs + results

Revision ID: 20250812_0001
Revises: None
Create Date: 2025-08-12 09:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250812_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # job_runs tablosu
    op.create_table(
        "job_runs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_type", sa.Text(), nullable=False),   # CHECK ile doğrulayacağız
        sa.Column("status", sa.Text(), nullable=False),     # CHECK ile doğrulayacağız
        sa.Column("input_payload", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("requested_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("task_id", sa.Text(), nullable=True, unique=True),
        sa.Column("trace_id", sa.Text(), nullable=True),
        sa.Column("metrics", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("idempotency_key", sa.Text(), nullable=True, unique=True),
        sa.CheckConstraint(
            "job_type IN ('os','katana')",
            name="ck_job_runs_job_type",
        ),
        sa.CheckConstraint(
            "status IN ('CREATED','QUEUED','STARTED','SUCCEEDED','FAILED','TIMEOUT','CANCELLED')",
            name="ck_job_runs_status",
        ),
    )

    op.create_index("ix_job_runs_requested_at", "job_runs", ["requested_at"])
    op.create_index("ix_job_runs_job_type_status", "job_runs", ["job_type", "status"])

    # results tablosu
    op.create_table(
        "results",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", sa.UUID(as_uuid=True), sa.ForeignKey("job_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("data", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_results_run_id", "results", ["run_id"])

    # updated_at trigger (opsiyonel, Postgres fonksiyonu)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_job_runs_updated_at
        BEFORE UPDATE ON job_runs
        FOR EACH ROW
        EXECUTE PROCEDURE set_updated_at();
        """
    )

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_job_runs_updated_at ON job_runs;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at;")
    op.drop_index("ix_results_run_id", table_name="results")
    op.drop_table("results")
    op.drop_index("ix_job_runs_job_type_status", table_name="job_runs")
    op.drop_index("ix_job_runs_requested_at", table_name="job_runs")
    op.drop_table("job_runs")
