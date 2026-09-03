from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from carveo_core.ingestion_contracts import ListingReference

TRACKING_PARAMETERS = {"fbclid", "gclid", "msclkid"}


class SourceIdentityError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class SourceIdentity:
    source_key: str
    source_listing_id: str
    canonical_url: str

    @property
    def key(self) -> str:
        return f"{self.source_key}:{self.source_listing_id}"


def canonicalize_source_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise SourceIdentityError("invalid_source_url") from exc
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower() if parsed.hostname else ""
    if scheme not in {"http", "https"} or not host:
        raise SourceIdentityError("invalid_source_url")
    if parsed.username is not None or parsed.password is not None:
        raise SourceIdentityError("invalid_source_url")

    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = host if port is None or default_port else f"{host}:{port}"
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query_values = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMETERS and not key.lower().startswith("utm_")
    ]
    query = urlencode(sorted(query_values))
    return urlunsplit((scheme, netloc, path, query, ""))


def resolve_source_identity(
    reference: ListingReference,
    *,
    canonical_url_matches: Sequence[str],
) -> SourceIdentity:
    canonical_url = canonicalize_source_url(reference.canonical_url)
    if reference.source_listing_id is not None:
        return SourceIdentity(reference.source_key, reference.source_listing_id, canonical_url)
    if len(canonical_url_matches) == 1:
        return SourceIdentity(reference.source_key, canonical_url_matches[0], canonical_url)
    if len(canonical_url_matches) > 1:
        raise SourceIdentityError("source_identity_ambiguous")
    raise SourceIdentityError("source_identity_missing")
