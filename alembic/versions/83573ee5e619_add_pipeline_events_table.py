"""add pipeline_events table

Revision ID: 83573ee5e619
Revises: 523a909e434c
Create Date: 2026-06-10 18:51:31.203289

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "83573ee5e619"
down_revision: Union[str, Sequence[str], None] = "523a909e434c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pipeline_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("node_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pipeline_events_run_id", "pipeline_events", ["run_id"], unique=False
    )
    op.create_index(
        "ix_pipeline_events_node_name", "pipeline_events", ["node_name"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_pipeline_events_node_name", table_name="pipeline_events")
    op.drop_index("ix_pipeline_events_run_id", table_name="pipeline_events")
    op.drop_table("pipeline_events")
