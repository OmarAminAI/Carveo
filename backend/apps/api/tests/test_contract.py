import json
from pathlib import Path

from carveo_api.main import app


def test_committed_openapi_document_is_current() -> None:
    contract = Path(__file__).parents[3] / "contracts" / "openapi.json"
    assert json.loads(contract.read_text(encoding="utf-8")) == app.openapi()


def test_buyer_workspace_contract_declares_bearer_security() -> None:
    schema = app.openapi()
    protected_operations = {
        "/api/v1/me/workspace": ["get"],
        "/api/v1/me/workspace/merge": ["post"],
        "/api/v1/me/shortlist/{listing_id}": ["put", "delete"],
        "/api/v1/me/comparison": ["put"],
        "/api/v1/me/saved-searches": ["get", "post"],
        "/api/v1/me/saved-searches/{saved_search_id}": ["delete"],
        "/api/v1/me/conversations": ["get", "post"],
        "/api/v1/me/conversations/{conversation_id}": ["get"],
        "/api/v1/me/conversations/{conversation_id}/turns": ["post"],
    }

    assert schema["components"]["securitySchemes"]["BearerAuth"] == {"type": "http", "scheme": "bearer"}
    for path, methods in protected_operations.items():
        for method in methods:
            assert schema["paths"][path][method]["security"] == [{"BearerAuth": []}]
    assert "security" not in schema["paths"]["/api/v1/listings"]["get"]
