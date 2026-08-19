import sys
from pathlib import Path

WORKER_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKER_ROOT))

from worker.main import main


def test_worker_smoke_starts_in_idle_mode() -> None:
    main(run_forever=False)


def test_worker_dockerfile_copies_importable_package() -> None:
    dockerfile = (WORKER_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY workers/ingestion/worker ./worker" in dockerfile
    assert 'CMD ["python", "-m", "worker.main"]' in dockerfile
