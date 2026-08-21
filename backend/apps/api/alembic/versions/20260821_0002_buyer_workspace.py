"""Create buyer workspace tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260821_0002"
down_revision: str | None = "20260820_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "buyer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_user_id", sa.String(255), nullable=False),
        sa.Column("anonymous_merged_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("clerk_user_id", name="uq_buyer_profiles_clerk_user_id"),
    )
    op.create_index("ix_buyer_profiles_clerk_user_id", "buyer_profiles", ["clerk_user_id"])
    op.create_table(
        "buyer_shortlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "buyer_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("buyer_profile_id", "listing_id", name="uq_buyer_shortlist_items_profile_listing"),
    )
    op.create_index("ix_buyer_shortlist_items_buyer_profile_id", "buyer_shortlist_items", ["buyer_profile_id"])
    op.create_table(
        "buyer_comparison_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "buyer_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("buyer_profile_id", "listing_id", name="uq_buyer_comparison_items_profile_listing"),
        sa.UniqueConstraint("buyer_profile_id", "position", name="uq_buyer_comparison_items_profile_position"),
        sa.CheckConstraint("position BETWEEN 0 AND 3", name="ck_buyer_comparison_items_position"),
    )
    op.create_index("ix_buyer_comparison_items_buyer_profile_id", "buyer_comparison_items", ["buyer_profile_id"])
    op.create_table(
        "buyer_saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "buyer_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("query", sa.String(2000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("buyer_profile_id", "query", name="uq_buyer_saved_searches_profile_query"),
    )
    op.create_index("ix_buyer_saved_searches_buyer_profile_id", "buyer_saved_searches", ["buyer_profile_id"])
    op.create_index(
        "ix_buyer_saved_searches_profile_updated_at",
        "buyer_saved_searches",
        ["buyer_profile_id", "updated_at"],
    )
    op.create_table(
        "buyer_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "buyer_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("client_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("interpreted_intent", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("buyer_profile_id", "client_id", name="uq_buyer_conversations_profile_client_id"),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_buyer_conversations_status"),
    )
    op.create_index("ix_buyer_conversations_buyer_profile_id", "buyer_conversations", ["buyer_profile_id"])
    op.create_index(
        "ix_buyer_conversations_profile_updated_at",
        "buyer_conversations",
        ["buyer_profile_id", "updated_at"],
    )
    op.create_table(
        "buyer_conversation_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("buyer_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.String(8000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("conversation_id", "sequence", name="uq_buyer_conversation_turns_conversation_sequence"),
        sa.CheckConstraint("sequence >= 0", name="ck_buyer_conversation_turns_sequence"),
        sa.CheckConstraint("role IN ('buyer', 'assistant')", name="ck_buyer_conversation_turns_role"),
    )
    op.create_index("ix_buyer_conversation_turns_conversation_id", "buyer_conversation_turns", ["conversation_id"])
    op.create_index(
        "ix_buyer_conversation_turns_conversation_sequence",
        "buyer_conversation_turns",
        ["conversation_id", "sequence"],
    )


def downgrade() -> None:
    op.drop_index("ix_buyer_conversation_turns_conversation_sequence", table_name="buyer_conversation_turns")
    op.drop_index("ix_buyer_conversation_turns_conversation_id", table_name="buyer_conversation_turns")
    op.drop_table("buyer_conversation_turns")
    op.drop_index("ix_buyer_conversations_profile_updated_at", table_name="buyer_conversations")
    op.drop_index("ix_buyer_conversations_buyer_profile_id", table_name="buyer_conversations")
    op.drop_table("buyer_conversations")
    op.drop_index("ix_buyer_saved_searches_profile_updated_at", table_name="buyer_saved_searches")
    op.drop_index("ix_buyer_saved_searches_buyer_profile_id", table_name="buyer_saved_searches")
    op.drop_table("buyer_saved_searches")
    op.drop_index("ix_buyer_comparison_items_buyer_profile_id", table_name="buyer_comparison_items")
    op.drop_table("buyer_comparison_items")
    op.drop_index("ix_buyer_shortlist_items_buyer_profile_id", table_name="buyer_shortlist_items")
    op.drop_table("buyer_shortlist_items")
    op.drop_index("ix_buyer_profiles_clerk_user_id", table_name="buyer_profiles")
    op.drop_table("buyer_profiles")
