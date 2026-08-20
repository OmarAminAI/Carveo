import json
from pathlib import Path

from carveo_api.main import app


def test_committed_openapi_document_is_current() -> None:
    contract = Path(__file__).parents[3] / "contracts" / "openapi.json"
    assert json.loads(contract.read_text(encoding="utf-8")) == app.openapi()
