"""init

Revision ID: 3bc883988942
Revises:
Create Date: 2026-06-09 20:57:55.312643

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "3bc883988942"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
