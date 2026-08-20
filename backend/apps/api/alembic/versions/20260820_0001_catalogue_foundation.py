"""Create catalogue foundation."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260820_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("market", sa.String(8), nullable=False),
        sa.Column("authorization_status", sa.String(32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("terms_reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("adapter_version", sa.String(40)),
        sa.Column("rate_limit_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_id", sa.String(160), nullable=False, unique=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("source_listing_id", sa.String(160), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("market", sa.String(8), nullable=False),
        sa.Column("lifecycle_status", sa.String(24), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("make", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("trim", sa.String(120), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("mileage_km", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(80), nullable=False),
        sa.Column("body_type", sa.String(48), nullable=False),
        sa.Column("specifications", sa.String(48), nullable=False),
        sa.Column("seller_type", sa.String(48), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("features", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("searchable_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_id", "source_listing_id", name="uq_listing_source_identity"),
    )
    op.create_index("ix_listings_market_status_freshness", "listings", ["market", "lifecycle_status", "last_seen_at"])
    op.create_index("ix_listings_make_model_year", "listings", ["make", "model", "year"])
    op.create_index("ix_listings_price", "listings", ["price"])
    op.create_index("ix_listings_mileage", "listings", ["mileage_km"])
    op.execute("CREATE INDEX ix_listings_search_fts ON listings USING gin (to_tsvector('simple', searchable_text))")
    op.execute("CREATE INDEX ix_listings_search_trgm ON listings USING gin (searchable_text gin_trgm_ops)")
    op.execute("CREATE INDEX ix_listings_source_identity ON listings (source_id, source_listing_id)")
    op.create_table(
        "listing_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("provenance", sa.String(80), nullable=False),
        sa.Column("source_media_id", sa.String(160)),
        sa.UniqueConstraint("listing_id", "position", name="uq_photo_position"),
    )
    op.create_table(
        "condition_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("source_claim", sa.Text()),
        sa.Column("confidence", sa.Float()),
    )
    op.create_index("ix_condition_evidence_listing_kind", "condition_evidence", ["listing_id", "kind"])
    op.create_table(
        "price_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("listing_id", "observed_at", name="uq_price_observation_time"),
    )
    op.create_table(
        "duplicate_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(160), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("duplicate_offers")
    op.drop_table("price_observations")
    op.drop_index("ix_condition_evidence_listing_kind", table_name="condition_evidence")
    op.drop_table("condition_evidence")
    op.drop_table("listing_photos")
    op.drop_table("listings")
    op.drop_table("sources")
