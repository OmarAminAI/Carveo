"""Create marketplace source, price observation, and saved-search tables."""

from alembic import op
import sqlalchemy as sa

revision = "20260819_02"
down_revision = "20260819_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("saved_searches", sa.Column("id", sa.String(length=36), nullable=False), sa.Column("profile_id", sa.String(length=80), nullable=False), sa.Column("name", sa.String(length=120), nullable=False), sa.Column("query", sa.JSON(), nullable=False), sa.Column("priority_refresh", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_saved_searches_profile_id", "saved_searches", ["profile_id"])
    op.create_table("sources", sa.Column("id", sa.String(length=64), nullable=False), sa.Column("market", sa.String(length=16), nullable=False), sa.Column("name", sa.String(length=120), nullable=False), sa.Column("status", sa.String(length=24), nullable=False), sa.Column("access_method", sa.String(length=32), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False), sa.Column("adapter_version", sa.String(length=32), nullable=True), sa.Column("terms_reviewed_at", sa.DateTime(timezone=True), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_sources_market", "sources", ["market"])
    op.create_table("price_observations", sa.Column("id", sa.String(length=36), nullable=False), sa.Column("listing_id", sa.String(length=96), nullable=False), sa.Column("price", sa.Integer(), nullable=False), sa.Column("currency", sa.String(length=8), nullable=False), sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_price_observations_listing_id", "price_observations", ["listing_id"])


def downgrade() -> None:
    op.drop_index("ix_price_observations_listing_id", table_name="price_observations"); op.drop_table("price_observations")
    op.drop_index("ix_sources_market", table_name="sources"); op.drop_table("sources")
    op.drop_index("ix_saved_searches_profile_id", table_name="saved_searches"); op.drop_table("saved_searches")
