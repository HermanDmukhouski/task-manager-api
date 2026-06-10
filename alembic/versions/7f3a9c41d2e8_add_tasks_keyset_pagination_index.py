"""add tasks keyset pagination index

Revision ID: 7f3a9c41d2e8
Revises: ba6bfb255145
Create Date: 2026-06-10 00:45:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f3a9c41d2e8"
down_revision: str | Sequence[str] | None = "ba6bfb255145"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f("ix_tasks_user_id_created_at_id"),
        "tasks",
        ["user_id", "created_at", "id"],
        unique=False,
    )
    op.drop_index(op.f("ix_tasks_user_id"), table_name="tasks")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(op.f("ix_tasks_user_id"), "tasks", ["user_id"], unique=False)
    op.drop_index(op.f("ix_tasks_user_id_created_at_id"), table_name="tasks")
