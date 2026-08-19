"""Create buyer-search session and message tables."""

from alembic import op
import sqlalchemy as sa

revision = "20260819_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("intent", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "search_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["search_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_messages_session_id", "search_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_search_messages_session_id", table_name="search_messages")
    op.drop_table("search_messages")
    op.drop_table("search_sessions")

