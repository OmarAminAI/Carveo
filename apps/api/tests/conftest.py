import os
import shutil
import tempfile
from pathlib import Path

TEST_DATABASE_DIR = Path(tempfile.mkdtemp(prefix="carveo-api-tests-"))
TEST_DATABASE_PATH = TEST_DATABASE_DIR / "carveo.db"
os.environ["CARVEO_DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"

import pytest

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


@pytest.fixture(scope="session", autouse=True)
def test_database() -> None:
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    shutil.rmtree(TEST_DATABASE_DIR, ignore_errors=True)
