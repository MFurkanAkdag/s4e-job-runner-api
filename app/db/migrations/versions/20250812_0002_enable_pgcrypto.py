# app/db/migrations/versions/20250812_0002_enable_pgcrypto.py
from alembic import op

revision = "20250812_0002"
down_revision = "20250812_0001"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
