from __future__ import annotations

from urllib.parse import urlsplit

from carveo_core.ingestion_contracts import SourceProfile


class SourcePolicyError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SourcePolicy:
    def authorize(self, profile: SourceProfile, environment: str, url: str) -> None:
        if profile.authorization_status == "blocked":
            raise SourcePolicyError("source_blocked")
        if profile.authorization_status not in {"fixture", "approved"}:
            raise SourcePolicyError("source_not_authorized")
        if not profile.enabled:
            raise SourcePolicyError("source_disabled")
        if profile.killed_at is not None:
            raise SourcePolicyError("source_killed")
        if profile.terms_reviewed_at is None:
            raise SourcePolicyError("terms_not_reviewed")
        if profile.authorization_status == "fixture" and environment == "production":
            raise SourcePolicyError("fixture_forbidden_in_production")
        if environment not in profile.environment_allowlist:
            raise SourcePolicyError("environment_not_allowed")

        try:
            parsed = urlsplit(url)
            host = parsed.hostname
        except ValueError as exc:
            raise SourcePolicyError("invalid_target_url") from exc
        if not parsed.scheme or not host:
            raise SourcePolicyError("invalid_target_url")
        if parsed.username is not None or parsed.password is not None:
            raise SourcePolicyError("url_credentials_forbidden")
        if parsed.scheme.lower() not in profile.allowed_schemes:
            raise SourcePolicyError("scheme_not_allowed")
        if host.lower() not in {allowed.lower() for allowed in profile.allowed_hosts}:
            raise SourcePolicyError("host_not_allowed")
