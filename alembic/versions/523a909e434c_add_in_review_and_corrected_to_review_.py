"""add_in_review_and_corrected_to_review_status

Revision ID: 523a909e434c
Revises: a1b2c3d4e5f6
Create Date: 2026-06-10 18:14:46.509656

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "523a909e434c"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ALTER TYPE ADD VALUE cannot run inside a transaction block in PostgreSQL under some conditions.
    # We execute with autocommit on or execute raw SQL commands directly.
    op.execute("ALTER TYPE reviewstatus ADD VALUE 'in_review'")
    op.execute("ALTER TYPE reviewstatus ADD VALUE 'corrected'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL does not support removing values from an ENUM type natively.
    pass
