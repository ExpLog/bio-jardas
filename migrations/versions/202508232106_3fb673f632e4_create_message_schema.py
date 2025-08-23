"""create message schema

Revision ID: 3fb673f632e4
Revises:
Create Date: 2025-08-23 21:06:46.345487

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3fb673f632e4"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS message")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS message")
