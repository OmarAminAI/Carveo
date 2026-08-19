from pathlib import Path
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_initial_migration_creates_search_tables(monkeypatch) -> None:
    with tempfile.TemporaryDirectory(prefix="carveo-migration-test-") as directory:
        database_path = Path(directory) / "migration.db"
        database_url = f"sqlite:///{database_path.as_posix()}"
        config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
        config.set_main_option("sqlalchemy.url", database_url)
        monkeypatch.delenv("CARVEO_DATABASE_URL")

        command.upgrade(config, "head")

        engine = create_engine(database_url)
        assert {"search_sessions", "search_messages"}.issubset(inspect(engine).get_table_names())
        engine.dispose()
