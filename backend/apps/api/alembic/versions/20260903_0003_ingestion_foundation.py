"""Add fixture-backed ingestion persistence."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_0003"
down_revision: str | None = "20260821_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("parser_version", sa.String(40)))
    op.add_column(
        "sources",
        sa.Column(
            "environment_allowlist",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "sources",
        sa.Column("allowed_hosts", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.add_column(
        "sources",
        sa.Column("allowed_schemes", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.add_column("sources", sa.Column("concurrency_limit", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("sources", sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False, server_default="30"))
    op.add_column("sources", sa.Column("killed_at", sa.DateTime(timezone=True)))
    op.add_column("sources", sa.Column("kill_reason", sa.String(240)))
    op.execute(
        """
        UPDATE sources
        SET terms_reviewed_at = COALESCE(terms_reviewed_at, TIMESTAMPTZ '2026-09-03 00:00:00+00'),
            adapter_version = COALESCE(adapter_version, 'fixture-v1'),
            parser_version = COALESCE(parser_version, 'fixture-parser-v1'),
            environment_allowlist = '["development", "test"]'::jsonb,
            allowed_hosts = '["fixture-origin"]'::jsonb,
            allowed_schemes = '["http"]'::jsonb
        WHERE key = 'carveo-fixture' AND authorization_status = 'fixture'
        """
    )
    op.create_check_constraint("ck_sources_concurrency_positive", "sources", "concurrency_limit > 0")
    op.create_check_constraint("ck_sources_rate_limit_positive", "sources", "rate_limit_per_minute > 0")

    op.add_column("listings", sa.Column("missing_at", sa.DateTime(timezone=True)))
    op.add_column(
        "listings",
        sa.Column("consecutive_successful_misses", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("listings", sa.Column("removed_at", sa.DateTime(timezone=True)))
    op.add_column("listings", sa.Column("source_sold_at", sa.DateTime(timezone=True)))
    op.add_column("listings", sa.Column("restored_at", sa.DateTime(timezone=True)))
    op.add_column("listings", sa.Column("purge_at", sa.DateTime(timezone=True)))
    op.create_check_constraint(
        "ck_listings_successful_misses_nonnegative",
        "listings",
        "consecutive_successful_misses >= 0",
    )
    op.create_index("ix_listings_lifecycle_purge", "listings", ["lifecycle_status", "purge_at"])

    op.add_column("listing_photos", sa.Column("source_url", sa.Text()))
    op.add_column("listing_photos", sa.Column("storage_key", sa.String(512)))
    op.add_column("listing_photos", sa.Column("content_hash", sa.String(64)))
    op.add_column("listing_photos", sa.Column("media_type", sa.String(80)))
    op.add_column("listing_photos", sa.Column("byte_size", sa.BigInteger()))
    op.add_column("listing_photos", sa.Column("refreshed_at", sa.DateTime(timezone=True)))
    op.add_column("listing_photos", sa.Column("purge_at", sa.DateTime(timezone=True)))
    op.execute("UPDATE listing_photos SET source_url = url WHERE source_url IS NULL")
    op.create_index("ix_listing_photos_content_hash", "listing_photos", ["content_hash"])
    op.create_index("ix_listing_photos_purge_at", "listing_photos", ["purge_at"])

    op.add_column("price_observations", sa.Column("market", sa.String(8)))
    op.add_column("price_observations", sa.Column("make", sa.String(100)))
    op.add_column("price_observations", sa.Column("model", sa.String(100)))
    op.add_column("price_observations", sa.Column("year", sa.Integer()))
    op.add_column("price_observations", sa.Column("specifications", sa.String(48)))
    op.add_column("price_observations", sa.Column("mileage_band_km", sa.Integer()))
    op.add_column("price_observations", sa.Column("currency", sa.String(3)))
    op.execute(
        """
        UPDATE price_observations AS observation
        SET market = listing.market,
            make = listing.make,
            model = listing.model,
            year = listing.year,
            specifications = listing.specifications,
            mileage_band_km = (listing.mileage_km / 10000) * 10000,
            currency = listing.currency
        FROM listings AS listing
        WHERE observation.listing_id = listing.id
        """
    )
    for column_name in ("market", "make", "model", "year", "specifications", "mileage_band_km", "currency"):
        op.alter_column("price_observations", column_name, nullable=False)
    op.drop_constraint("price_observations_listing_id_fkey", "price_observations", type_="foreignkey")
    op.alter_column("price_observations", "listing_id", nullable=True)
    op.create_foreign_key(
        "price_observations_listing_id_fkey",
        "price_observations",
        "listings",
        ["listing_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_price_observations_market_model_time",
        "price_observations",
        ["market", "make", "model", "observed_at"],
    )

    for table_name in ("buyer_shortlist_items", "buyer_comparison_items"):
        constraint_name = f"{table_name}_listing_id_fkey"
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")
        op.create_foreign_key(
            constraint_name,
            table_name,
            "listings",
            ["listing_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.create_table(
        "crawl_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("query_key", sa.String(120), nullable=False),
        sa.Column("fixture_scenario", sa.String(80), nullable=False),
        sa.Column("trigger", sa.String(24), nullable=False),
        sa.Column("correlation_key", sa.String(240), nullable=False),
        sa.Column("adapter_version", sa.String(40), nullable=False),
        sa.Column("parser_version", sa.String(40), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("discovery_complete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("counters", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("error_code", sa.String(80)),
        sa.Column("purge_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("correlation_key", name="uq_crawl_runs_correlation_key"),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'partially_completed', 'failed')",
            name="ck_crawl_runs_status",
        ),
    )
    op.create_index("ix_crawl_runs_source_status", "crawl_runs", ["source_id", "status"])
    op.create_index("ix_crawl_runs_started_at", "crawl_runs", ["started_at"])
    op.create_index("ix_crawl_runs_purge_at", "crawl_runs", ["purge_at"])

    op.create_table(
        "crawl_run_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crawl_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("identity_key", sa.String(512), nullable=False),
        sa.Column("source_listing_id", sa.String(160)),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("search_page_key", sa.String(160), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="SET NULL")),
        sa.Column("fetch_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("parse_status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_fingerprint", sa.String(64)),
        sa.Column("error_code", sa.String(80)),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("run_id", "identity_key", name="uq_crawl_run_items_run_identity"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_crawl_run_items_attempt_count"),
    )
    op.create_index(
        "ix_crawl_run_items_run_status", "crawl_run_items", ["run_id", "fetch_status", "parse_status"]
    )
    op.create_index("ix_crawl_run_items_listing_id", "crawl_run_items", ["listing_id"])

    op.create_table(
        "extraction_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crawl_run_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="SET NULL")),
        sa.Column("extraction_payload", postgresql.JSONB(), nullable=False),
        sa.Column("extraction_evidence", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("parser_version", sa.String(40), nullable=False),
        sa.Column("content_fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("purge_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_extraction_artifacts_purge_at", "extraction_artifacts", ["purge_at"])


def downgrade() -> None:
    op.drop_index("ix_extraction_artifacts_purge_at", table_name="extraction_artifacts")
    op.drop_table("extraction_artifacts")
    op.drop_index("ix_crawl_run_items_listing_id", table_name="crawl_run_items")
    op.drop_index("ix_crawl_run_items_run_status", table_name="crawl_run_items")
    op.drop_table("crawl_run_items")
    op.drop_index("ix_crawl_runs_purge_at", table_name="crawl_runs")
    op.drop_index("ix_crawl_runs_started_at", table_name="crawl_runs")
    op.drop_index("ix_crawl_runs_source_status", table_name="crawl_runs")
    op.drop_table("crawl_runs")

    for table_name in ("buyer_shortlist_items", "buyer_comparison_items"):
        constraint_name = f"{table_name}_listing_id_fkey"
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")
        op.create_foreign_key(constraint_name, table_name, "listings", ["listing_id"], ["id"])

    op.drop_index("ix_price_observations_market_model_time", table_name="price_observations")
    op.execute("DELETE FROM price_observations WHERE listing_id IS NULL")
    op.drop_constraint("price_observations_listing_id_fkey", "price_observations", type_="foreignkey")
    op.alter_column("price_observations", "listing_id", nullable=False)
    op.create_foreign_key(
        "price_observations_listing_id_fkey",
        "price_observations",
        "listings",
        ["listing_id"],
        ["id"],
        ondelete="CASCADE",
    )
    for column_name in ("currency", "mileage_band_km", "specifications", "year", "model", "make", "market"):
        op.drop_column("price_observations", column_name)

    op.drop_index("ix_listing_photos_purge_at", table_name="listing_photos")
    op.drop_index("ix_listing_photos_content_hash", table_name="listing_photos")
    for column_name in (
        "purge_at",
        "refreshed_at",
        "byte_size",
        "media_type",
        "content_hash",
        "storage_key",
        "source_url",
    ):
        op.drop_column("listing_photos", column_name)

    op.drop_index("ix_listings_lifecycle_purge", table_name="listings")
    op.drop_constraint("ck_listings_successful_misses_nonnegative", "listings", type_="check")
    for column_name in (
        "purge_at",
        "restored_at",
        "source_sold_at",
        "removed_at",
        "consecutive_successful_misses",
        "missing_at",
    ):
        op.drop_column("listings", column_name)

    op.drop_constraint("ck_sources_rate_limit_positive", "sources", type_="check")
    op.drop_constraint("ck_sources_concurrency_positive", "sources", type_="check")
    for column_name in (
        "kill_reason",
        "killed_at",
        "rate_limit_per_minute",
        "concurrency_limit",
        "allowed_schemes",
        "allowed_hosts",
        "environment_allowlist",
        "parser_version",
    ):
        op.drop_column("sources", column_name)
