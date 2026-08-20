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
                "sources",
                "listings",
                "listing_photos",
                "condition_evidence",
                "price_observations",
                "duplicate_offers",
            }
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT extname FROM pg_extension WHERE extname='pg_trgm'")) == "pg_trgm"
    except DockerException:
        pytest.skip("Docker is required for PostgreSQL migration tests")
