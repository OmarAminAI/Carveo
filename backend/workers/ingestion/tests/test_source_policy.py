from datetime import UTC, datetime
from uuid import uuid4

import pytest
from carveo_core.ingestion_contracts import SourceProfile
from carveo_worker.source_policy import SourcePolicy, SourcePolicyError

FIXTURE_URL = "http://fixture-origin:8080/listings/fixture-001.html"
NOW = datetime(2026, 9, 3, tzinfo=UTC)


def profile_with(**changes: object) -> SourceProfile:
    values: dict[str, object] = {
        "id": uuid4(),
        "key": "carveo-fixture",
        "market": "ae",
        "authorization_status": "fixture",
        "enabled": True,
        "environment_allowlist": ["development", "test"],
        "allowed_hosts": ["fixture-origin"],
        "allowed_schemes": ["http"],
        "terms_reviewed_at": NOW,
        "adapter_version": "fixture-v1",
        "parser_version": "fixture-parser-v1",
        "concurrency_limit": 2,
        "rate_limit_per_minute": 30,
        "killed_at": None,
        "kill_reason": None,
    }
    values.update(changes)
    return SourceProfile.model_validate(values)


@pytest.mark.parametrize(
    ("change", "error_code"),
    [
        ({"enabled": False}, "source_disabled"),
        ({"authorization_status": "pending"}, "source_not_authorized"),
        ({"authorization_status": "blocked"}, "source_blocked"),
        ({"environment_allowlist": ["test"]}, "environment_not_allowed"),
        ({"killed_at": NOW}, "source_killed"),
        ({"terms_reviewed_at": None}, "terms_not_reviewed"),
    ],
)
def test_policy_rejects_before_fetch(change: dict[str, object], error_code: str) -> None:
    with pytest.raises(SourcePolicyError) as raised:
        SourcePolicy().authorize(profile_with(**change), "development", FIXTURE_URL)

    assert raised.value.code == error_code


def test_fixture_source_is_forbidden_in_production() -> None:
    profile = profile_with(environment_allowlist=["development", "test", "production"])

    with pytest.raises(SourcePolicyError) as raised:
        SourcePolicy().authorize(profile, "production", FIXTURE_URL)

    assert raised.value.code == "fixture_forbidden_in_production"


@pytest.mark.parametrize(
    ("url", "error_code"),
    [
        ("https://fixture-origin/listings/1", "scheme_not_allowed"),
        ("http://example.com/listings/1", "host_not_allowed"),
        ("http://user:password@fixture-origin/listings/1", "url_credentials_forbidden"),
        ("http:///listings/1", "invalid_target_url"),
    ],
)
def test_policy_rejects_unapproved_targets(url: str, error_code: str) -> None:
    with pytest.raises(SourcePolicyError) as raised:
        SourcePolicy().authorize(profile_with(), "development", url)

    assert raised.value.code == error_code


@pytest.mark.parametrize("environment", ["development", "test"])
def test_policy_allows_fixture_origin_only_in_non_production(environment: str) -> None:
    SourcePolicy().authorize(profile_with(), environment, FIXTURE_URL)


def test_policy_allows_approved_source_in_its_allowlisted_production_environment() -> None:
    profile = profile_with(
        authorization_status="approved",
        environment_allowlist=["production"],
        allowed_hosts=["feed.example.ae"],
        allowed_schemes=["https"],
    )

    SourcePolicy().authorize(profile, "production", "https://feed.example.ae/listings/1")
