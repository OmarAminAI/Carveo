import os
import subprocess

import pytest
from docker.errors import DockerException
from sqlalchemy import create_engine, inspect, text
from testcontainers.postgres import PostgresContainer


@pytest.mark.integration
def test_fresh_postgres_migrates_to_head() -> None:
    try:
        with PostgresContainer("postgres:18-alpine") as postgres:
            sync_url = postgres.get_connection_url().replace("psycopg2", "psycopg")
            env = {**os.environ, "CARVEO_DATABASE_URL": sync_url.replace("postgresql+psycopg", "postgresql+psycopg")}
            subprocess.run(
                ["uv", "run", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
                check=True,
                env=env,
            )
            engine = create_engine(sync_url)
            assert set(inspect(engine).get_table_names()) >= {
                "buyer_profiles",
                "buyer_shortlist_items",
                "buyer_comparison_items",
                "buyer_saved_searches",
                "buyer_conversations",
                "buyer_conversation_turns",
                "sources",
                "listings",
                "listing_photos",
                "condition_evidence",
                "crawl_run_items",
                "crawl_runs",
                "price_observations",
                "duplicate_offers",
                "extraction_artifacts",
            }
            inspector = inspect(engine)
            assert {"clerk_user_id"} in _unique_column_sets(inspector, "buyer_profiles")
            assert {"buyer_profile_id", "listing_id"} in _unique_column_sets(inspector, "buyer_shortlist_items")
            assert {"buyer_profile_id", "listing_id"} in _unique_column_sets(inspector, "buyer_comparison_items")
            assert {"buyer_profile_id", "position"} in _unique_column_sets(inspector, "buyer_comparison_items")
            assert {"buyer_profile_id", "query"} in _unique_column_sets(inspector, "buyer_saved_searches")
            assert {"buyer_profile_id", "client_id"} in _unique_column_sets(inspector, "buyer_conversations")
            assert {"conversation_id", "sequence"} in _unique_column_sets(inspector, "buyer_conversation_turns")
            assert {"correlation_key"} in _unique_column_sets(inspector, "crawl_runs")
            assert {"run_id", "identity_key"} in _unique_column_sets(inspector, "crawl_run_items")
            assert _foreign_key_targets(inspector, "buyer_shortlist_items") == {"buyer_profiles", "listings"}
            assert _foreign_key_targets(inspector, "buyer_comparison_items") == {"buyer_profiles", "listings"}
            assert _foreign_key_targets(inspector, "buyer_saved_searches") == {"buyer_profiles"}
            assert _foreign_key_targets(inspector, "buyer_conversations") == {"buyer_profiles"}
            assert _foreign_key_targets(inspector, "buyer_conversation_turns") == {"buyer_conversations"}
            assert _foreign_key_targets(inspector, "crawl_runs") == {"sources"}
            assert _foreign_key_targets(inspector, "crawl_run_items") == {"crawl_runs", "listings"}
            assert _foreign_key_targets(inspector, "extraction_artifacts") == {"crawl_run_items", "listings"}
            assert _foreign_key_ondelete(inspector, "buyer_shortlist_items") == {
                "buyer_profiles": "CASCADE",
                "listings": "CASCADE",
            }
            assert _foreign_key_ondelete(inspector, "buyer_comparison_items") == {
                "buyer_profiles": "CASCADE",
                "listings": "CASCADE",
            }
            assert _foreign_key_ondelete(inspector, "price_observations") == {"listings": "SET NULL"}
            assert _foreign_key_ondelete(inspector, "buyer_saved_searches") == {"buyer_profiles": "CASCADE"}
            assert _foreign_key_ondelete(inspector, "buyer_conversations") == {"buyer_profiles": "CASCADE"}
            assert _foreign_key_ondelete(inspector, "buyer_conversation_turns") == {"buyer_conversations": "CASCADE"}
            assert {
                "ix_buyer_profiles_clerk_user_id",
                "ix_buyer_shortlist_items_buyer_profile_id",
                "ix_buyer_comparison_items_buyer_profile_id",
                "ix_buyer_saved_searches_buyer_profile_id",
                "ix_buyer_saved_searches_profile_updated_at",
                "ix_buyer_conversations_buyer_profile_id",
                "ix_buyer_conversations_profile_updated_at",
                "ix_buyer_conversation_turns_conversation_id",
                "ix_buyer_conversation_turns_conversation_sequence",
                "ix_crawl_runs_source_status",
                "ix_crawl_runs_started_at",
                "ix_crawl_runs_purge_at",
                "ix_crawl_run_items_run_status",
                "ix_crawl_run_items_listing_id",
                "ix_extraction_artifacts_purge_at",
                "ix_listings_lifecycle_purge",
                "ix_listing_photos_content_hash",
                "ix_listing_photos_purge_at",
                "ix_price_observations_market_model_time",
            } <= _index_names(inspector)
            assert {"ck_buyer_comparison_items_position"} <= _check_constraint_names(
                inspector, "buyer_comparison_items"
            )
            assert {"ck_buyer_conversations_status"} <= _check_constraint_names(inspector, "buyer_conversations")
            assert {
                "ck_buyer_conversation_turns_role",
                "ck_buyer_conversation_turns_sequence",
            } <= _check_constraint_names(inspector, "buyer_conversation_turns")
            assert {"ck_crawl_runs_status"} <= _check_constraint_names(inspector, "crawl_runs")
            assert {"ck_crawl_run_items_attempt_count"} <= _check_constraint_names(inspector, "crawl_run_items")
            assert {"ck_listings_successful_misses_nonnegative"} <= _check_constraint_names(inspector, "listings")
            assert {
                "ck_sources_concurrency_positive",
                "ck_sources_rate_limit_positive",
            } <= _check_constraint_names(inspector, "sources")
            price_columns = {column["name"]: column for column in inspector.get_columns("price_observations")}
            assert price_columns["listing_id"]["nullable"] is True
            assert {
                "market",
                "make",
                "model",
                "year",
                "specifications",
                "mileage_band_km",
                "currency",
            } <= set(price_columns)
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT extname FROM pg_extension WHERE extname='pg_trgm'")) == "pg_trgm"
            subprocess.run(
                ["uv", "run", "alembic", "-c", "apps/api/alembic.ini", "downgrade", "20260820_0001"],
                check=True,
                env=env,
            )
            assert not {
                "buyer_profiles",
                "buyer_shortlist_items",
                "buyer_comparison_items",
                "buyer_saved_searches",
                "buyer_conversations",
                "buyer_conversation_turns",
            } & set(inspect(engine).get_table_names())
    except DockerException:
        pytest.skip("Docker is required for PostgreSQL migration tests")


def _unique_column_sets(inspector: object, table_name: str) -> list[set[str]]:
    return [set(constraint["column_names"]) for constraint in inspector.get_unique_constraints(table_name)]  # type: ignore[union-attr]


def _foreign_key_targets(inspector: object, table_name: str) -> set[str]:
    return {
        foreign_key["referred_table"]
        for foreign_key in inspector.get_foreign_keys(table_name)  # type: ignore[union-attr]
    }


def _foreign_key_ondelete(inspector: object, table_name: str) -> dict[str, str | None]:
    return {
        foreign_key["referred_table"]: foreign_key.get("options", {}).get("ondelete")
        for foreign_key in inspector.get_foreign_keys(table_name)  # type: ignore[union-attr]
    }


def _index_names(inspector: object) -> set[str]:
    return {
        index["name"]
        for table_name in (
            "buyer_profiles",
            "buyer_shortlist_items",
            "buyer_comparison_items",
            "buyer_saved_searches",
            "buyer_conversations",
            "buyer_conversation_turns",
            "crawl_runs",
            "crawl_run_items",
            "extraction_artifacts",
            "listings",
            "listing_photos",
            "price_observations",
        )
        for index in inspector.get_indexes(table_name)  # type: ignore[union-attr]
    }


def _check_constraint_names(inspector: object, table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in inspector.get_check_constraints(table_name)  # type: ignore[union-attr]
    }
