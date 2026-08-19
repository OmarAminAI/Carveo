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


def test_readiness_confirms_test_database() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").json() == {"status": "ready"}


def test_catalogue_can_filter_compare_and_save_anonymous_search() -> None:
    profile_id = "browser-profile-123456789"
    with TestClient(app) as client:
        listings = client.get("/api/v1/listings", params={"market": "AE", "make": "Mercedes-Benz", "price_max": 180000})
        assert listings.status_code == 200
        payload = listings.json()
        assert payload["total"] == 3
        assert payload["items"][0]["typical_price"] is not None
        assert payload["items"][0]["condition"]

        detail = client.get("/api/v1/listings/ae-001")
        assert detail.status_code == 200
        assert detail.json()["deal_label"] in {"Great deal", "Good deal", "Fair price", "Verify price"}

        comparison = client.post("/api/v1/compare", json={"listing_ids": ["ae-001", "ae-002"]})
        assert comparison.status_code == 200
        assert len(comparison.json()["listings"]) == 2

        saved = client.put("/api/v1/profile/searches", json={"profile_id": profile_id, "name": "C-Class search", "query": {"make": "Mercedes-Benz"}, "priority_refresh": True})
        assert saved.status_code == 201
        saved_id = saved.json()["id"]
        assert client.get("/api/v1/profile/searches", params={"profile_id": profile_id}).json()[0]["id"] == saved_id
        assert client.delete(f"/api/v1/profile/searches/{saved_id}", params={"profile_id": profile_id}).status_code == 204
