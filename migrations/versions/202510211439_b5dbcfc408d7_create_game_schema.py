"""create game schema

Revision ID: b5dbcfc408d7
Revises: c276d5ad20b3
Create Date: 2025-10-21 14:39:41.553560

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5dbcfc408d7"
down_revision: str | Sequence[str] | None = "c276d5ad20b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS game")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS game")
