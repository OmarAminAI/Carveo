from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from carveo_core.ingestion_contracts import (
    ListingReference,
    RawListing,
    RawPhoto,
    RejectedListing,
    SourceProfile,
    SourceQuery,
)

from carveo_worker.adapters.base import DiscoveryResult
from carveo_worker.crawl4ai_client import Crawl4AIClient
from carveo_worker.identity import canonicalize_source_url
from carveo_worker.source_policy import SourcePolicy


class _SearchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.complete = False
        self.links: list[tuple[str | None, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "body":
            self.complete = values.get("data-discovery-complete") == "true"
        if tag == "a" and values.get("href") and "data-source-listing-id" in values:
            self.links.append((values.get("data-source-listing-id"), values["href"] or ""))


class _DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.json_ld_blocks: list[str] = []
        self.values: dict[str, str] = {}
        self.photos: list[str] = []
        self._json_ld_parts: list[str] | None = None
        self._field: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        script_type = values.get("type")
        if tag == "script" and isinstance(script_type, str) and script_type.lower() == "application/ld+json":
            self._json_ld_parts = []
            return
        if tag == "img" and "data-carveo-photo" in values and values.get("src"):
            self.photos.append(values["src"] or "")
        for name in values:
            if name.startswith("data-carveo-") and name != "data-carveo-photo":
                self._field = name.removeprefix("data-carveo-").replace("-", "_")
                break

    def handle_data(self, data: str) -> None:
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
        elif self._field is not None:
            self.values[self._field] = self.values.get(self._field, "") + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld_parts is not None:
            self.json_ld_blocks.append("".join(self._json_ld_parts).strip())
            self._json_ld_parts = None
        self._field = None


class FixtureSourceAdapter:
    def __init__(
        self,
        *,
        profile: SourceProfile,
        policy: SourcePolicy,
        client: Crawl4AIClient,
        environment: str,
        manifest: Mapping[str, Any],
        clock: Callable[[], datetime],
    ) -> None:
        self._profile = profile
        self._policy = policy
        self._client = client
        self._environment = environment
        self._manifest = manifest
        self._clock = clock

    @classmethod
    def from_manifest_path(
        cls,
        *,
        profile: SourceProfile,
        policy: SourcePolicy,
        client: Crawl4AIClient,
        environment: str,
        manifest_path: Path,
        clock: Callable[[], datetime],
    ) -> FixtureSourceAdapter:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("fixture manifest is unavailable or invalid") from exc
        if not isinstance(manifest, Mapping):
            raise ValueError("fixture manifest must be an object")
        return cls(
            profile=profile,
            policy=policy,
            client=client,
            environment=environment,
            manifest=manifest,
            clock=clock,
        )

    async def discover(self, query: SourceQuery) -> DiscoveryResult:
        page_urls = self._scenario_pages(query)
        for url in page_urls:
            self._policy.authorize(self._profile, self._environment, url)
        documents = await self._client.crawl(page_urls)

        references: list[ListingReference] = []
        seen: set[str] = set()
        complete = len(documents) == len(page_urls)
        error_code: str | None = None
        for page_number, document in enumerate(documents, start=1):
            if not document.success:
                complete = False
                error_code = error_code or document.error or "discovery_failed"
                continue
            parser = _SearchParser()
            parser.feed(document.html)
            complete = complete and parser.complete
            if not parser.complete:
                error_code = error_code or "incomplete_discovery"
            for source_listing_id, href in parser.links:
                canonical_url = canonicalize_source_url(urljoin(document.url, href))
                identity = source_listing_id or canonical_url
                if identity in seen:
                    continue
                seen.add(identity)
                references.append(
                    ListingReference(
                        source_key=self._profile.key,
                        source_listing_id=source_listing_id,
                        canonical_url=canonical_url,
                        discovered_at=self._clock(),
                        search_page_key=f"{query.query_key}:{query.fixture_scenario}:{page_number}",
                    )
                )
        return DiscoveryResult(
            references=references,
            visited_pages=page_urls,
            discovery_complete=complete,
            error_code=error_code,
        )

    async def extract(self, reference: ListingReference) -> RawListing | RejectedListing:
        if reference.source_key != self._profile.key:
            return self._reject(reference, "source_mismatch", "Reference belongs to another source")
        self._policy.authorize(self._profile, self._environment, reference.canonical_url)
        documents = await self._client.crawl([reference.canonical_url])
        if len(documents) != 1 or not documents[0].success:
            error = documents[0].error if documents else "invalid_response"
            return self._reject(reference, error or "extraction_failed", "Source document could not be retrieved")

        parser = _DetailParser()
        parser.feed(documents[0].html)
        if parser.json_ld_blocks:
            return self._extract_json_ld(reference, parser.json_ld_blocks)
        return self._extract_css(reference, parser)

    def _scenario_pages(self, query: SourceQuery) -> list[str]:
        if self._manifest.get("sourceKey") != self._profile.key or self._manifest.get("queryKey") != query.query_key:
            raise ValueError("fixture manifest does not match source query")
        scenarios = self._manifest.get("scenarios")
        scenario = scenarios.get(query.fixture_scenario) if isinstance(scenarios, Mapping) else None
        pages = scenario.get("searchPages") if isinstance(scenario, Mapping) else None
        if not isinstance(pages, list) or not pages or not all(isinstance(page, str) for page in pages):
            raise ValueError("fixture scenario has no valid search pages")
        return list(pages)

    def _extract_json_ld(
        self,
        reference: ListingReference,
        blocks: list[str],
    ) -> RawListing | RejectedListing:
        try:
            candidates = [json.loads(block) for block in blocks]
        except ValueError:
            return self._reject(reference, "malformed_json_ld", "JSON-LD could not be parsed")
        vehicle = next((found for candidate in candidates if (found := _find_vehicle(candidate)) is not None), None)
        if vehicle is None:
            return self._reject(reference, "vehicle_data_missing", "JSON-LD does not contain a vehicle")

        raw_offers = vehicle.get("offers")
        offers: Mapping[str, Any] = raw_offers if isinstance(raw_offers, Mapping) else {}
        raw_mileage = vehicle.get("mileageFromOdometer")
        mileage_values: Mapping[object, object] = raw_mileage if isinstance(raw_mileage, Mapping) else {}
        properties = _additional_properties(vehicle.get("additionalProperty"))
        images = vehicle.get("image", [])
        if isinstance(images, str):
            images = [images]
        photo_urls = [image for image in images if isinstance(image, str)] if isinstance(images, list) else []
        availability = str(offers.get("availability", "")).lower()
        return RawListing(
            reference=reference,
            title=_text(vehicle.get("name")),
            make=_brand_name(vehicle.get("brand")),
            model=_text(vehicle.get("model")),
            trim=properties.get("trim"),
            year=_text(vehicle.get("vehicleModelDate")),
            price=_text(offers.get("price")),
            currency=_text(offers.get("priceCurrency")),
            mileage=_measurement(mileage_values),
            city=properties.get("city"),
            body_type=properties.get("bodyType"),
            specifications=properties.get("specifications"),
            seller_type=properties.get("sellerType"),
            description=_text(vehicle.get("description")) or "",
            photos=[RawPhoto(source_url=url) for url in photo_urls],
            source_sold=any(marker in availability for marker in ("soldout", "outofstock", "discontinued")),
            extraction_path="json-ld",
            extracted_at=self._clock(),
        )

    def _extract_css(self, reference: ListingReference, parser: _DetailParser) -> RawListing | RejectedListing:
        values = {key: value.strip() for key, value in parser.values.items()}
        if not values.get("title"):
            return self._reject(reference, "vehicle_data_missing", "CSS selectors did not yield a vehicle")
        return RawListing(
            reference=reference,
            title=values.get("title"),
            make=values.get("make"),
            model=values.get("model"),
            trim=values.get("trim"),
            year=values.get("year"),
            price=values.get("price"),
            currency="AED" if (values.get("price") or "").upper().startswith("AED") else None,
            mileage=values.get("mileage"),
            city=values.get("city"),
            body_type=values.get("body_type"),
            specifications=values.get("specifications"),
            seller_type=values.get("seller_type"),
            description=values.get("description", ""),
            photos=[RawPhoto(source_url=url) for url in parser.photos],
            source_sold=values.get("availability", "").lower() == "sold",
            extraction_path="css",
            extracted_at=self._clock(),
        )

    @staticmethod
    def _reject(reference: ListingReference, code: str, detail: str) -> RejectedListing:
        return RejectedListing(reference=reference, error_code=code[:80], detail=detail[:400])


def _find_vehicle(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        if value.get("@type") == "Vehicle":
            return value
        graph = value.get("@graph")
        if isinstance(graph, list):
            return next((item for item in graph if isinstance(item, Mapping) and item.get("@type") == "Vehicle"), None)
    if isinstance(value, list):
        return next((item for item in value if isinstance(item, Mapping) and item.get("@type") == "Vehicle"), None)
    return None


def _additional_properties(value: object) -> dict[str, str]:
    if not isinstance(value, list):
        return {}
    properties: dict[str, str] = {}
    for item in value:
        if not isinstance(item, Mapping):
            continue
        name = item.get("name")
        item_value = item.get("value")
        if isinstance(name, str) and isinstance(item_value, (str, int, float)):
            properties[name] = str(item_value)
    return properties


def _text(value: object) -> str | None:
    return str(value) if isinstance(value, (str, int, float)) else None


def _brand_name(value: object) -> str | None:
    if isinstance(value, Mapping):
        return _text(value.get("name"))
    return _text(value)


def _measurement(value: Mapping[object, object]) -> str | None:
    amount = _text(value.get("value"))
    unit = _text(value.get("unitCode"))
    if amount is None:
        return None
    return f"{amount} {unit}" if unit else amount
