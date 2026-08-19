from fastapi.testclient import TestClient

from app.main import app


def test_buyer_can_complete_fixture_search() -> None:
    with TestClient(app) as client:
        session = client.post("/api/v1/sessions")
        assert session.status_code == 201
        session_id = session.json()["session_id"]

        message = client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "2023 Mercedes C-Class in UAE under AED 180k, black, GCC specs, accident-free, under 50k km"},
        )
        assert message.status_code == 200
        assert message.json()["intent_state"]["ready"] is True

        results = client.get(f"/api/v1/sessions/{session_id}/results")
        assert results.status_code == 200
        assert results.json()["matches"][0]["listing"]["id"] == "dubizzle-fixture-1"


def test_results_reject_incomplete_intent() -> None:
    with TestClient(app) as client:
        session_id = client.post("/api/v1/sessions").json()["session_id"]
        response = client.get(f"/api/v1/sessions/{session_id}/results")

    assert response.status_code == 409
