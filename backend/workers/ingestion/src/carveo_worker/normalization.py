from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal
from urllib.parse import urlsplit

from carveo_core.ingestion_contracts import (
    NormalizedConditionEvidence,
    NormalizedListing,
    NormalizedPhoto,
    RawConditionClaim,
    RawListing,
    RejectedListing,
)
from pydantic import ValidationError

from carveo_worker.identity import SourceIdentityError, canonicalize_source_url

Currency = Literal["AED"]
City = Literal["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
BodyType = Literal["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"]
Specifications = Literal["GCC", "American", "European", "Japanese"]
SellerType = Literal["Dealer", "Private"]


class NormalizationError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(code)


def normalize_listing(raw: RawListing, now: datetime) -> NormalizedListing | RejectedListing:
    try:
        canonical_url = canonicalize_source_url(raw.reference.canonical_url)
        title = _required(raw.title, "title")
        make = _required(raw.make, "make")
        model = _required(raw.model, "model")
        trim = _required(raw.trim, "trim")
        year = normalize_year(raw.year, now)
        price = normalize_price(raw.price)
        currency = normalize_currency(raw.currency, raw.price)
        mileage_km = normalize_mileage(raw.mileage)
        city = normalize_city(raw.city)
        body_type = normalize_body_type(raw.body_type)
        specifications = normalize_specifications(raw.specifications)
        seller_type = normalize_seller_type(raw.seller_type)
        photos = normalize_photos(raw)
        evidence = normalize_condition_evidence(raw.condition_claims)
        normalized_reference = raw.reference.model_copy(update={"canonical_url": canonical_url})
        return NormalizedListing(
            reference=normalized_reference,
            market="ae",
            title=title,
            make=make,
            model=model,
            trim=trim,
            year=year,
            price=price,
            currency=currency,
            mileage_km=mileage_km,
            city=city,
            body_type=body_type,
            specifications=specifications,
            seller_type=seller_type,
            description=raw.description,
            features=list(raw.features),
            photos=photos,
            condition_evidence=evidence,
            source_sold=raw.source_sold,
            original_values=_original_values(raw),
            extracted_at=raw.extracted_at,
        )
    except SourceIdentityError:
        return _reject(raw, "invalid_source_url", "Source listing URL is invalid")
    except NormalizationError as exc:
        return _reject(raw, exc.code, exc.detail)
    except ValidationError:
        return _reject(raw, "invalid_normalized_listing", "Normalized listing does not satisfy the catalogue contract")


def normalize_price(value: str | None) -> int:
    text = _required(value, "price")
    match = re.search(r"\d[\d,\s]*(?:\.\d+)?", text)
    if match is None:
        raise NormalizationError("invalid_price", "Price is not a supported AED amount")
    numeric = match.group(0).replace(",", "").replace(" ", "")
    try:
        amount = Decimal(numeric)
    except InvalidOperation as exc:
        raise NormalizationError("invalid_price", "Price is not a supported AED amount") from exc
    if amount < 0 or amount != amount.to_integral_value():
        raise NormalizationError("invalid_price", "Price must be a non-negative whole AED amount")
    return int(amount)


def normalize_currency(value: str | None, price_text: str | None) -> Currency:
    candidate = (value or "").strip().upper()
    if not candidate and price_text and re.search(r"\bAED\b", price_text, re.IGNORECASE):
        candidate = "AED"
    if not candidate:
        raise NormalizationError("missing_currency", "Currency is required")
    if candidate not in {"AED", "DH", "DHS", "DIRHAM", "DIRHAMS"}:
        raise NormalizationError("unsupported_currency", "Only AED source prices are supported")
    return "AED"


def normalize_mileage(value: str | None) -> int:
    text = _required(value, "mileage")
    match = re.fullmatch(
        r"\s*(\d[\d,\s]*)\s*(km|kms|kmt|kilometre|kilometres|kilometer|kilometers)\s*",
        text,
        re.IGNORECASE,
    )
    if match is None:
        unit = re.search(r"[A-Za-z]+", text)
        code = "unsupported_mileage_unit" if unit else "invalid_mileage"
        raise NormalizationError(code, "Mileage must use kilometres")
    return int(match.group(1).replace(",", "").replace(" ", ""))


def normalize_year(value: str | None, now: datetime) -> int:
    text = _required(value, "year")
    match = re.search(r"(?<!\d)(\d{4})(?!\d)", text)
    if match is None:
        raise NormalizationError("invalid_year", "Model year is invalid")
    year = int(match.group(1))
    if year < 1900 or year > now.year + 1:
        raise NormalizationError("invalid_year", "Model year is outside the supported range")
    return year


def normalize_city(value: str | None) -> City:
    text = _required(value, "city")
    key = _alias_key(text)
    aliases: dict[str, City] = {
        "dubai": "Dubai",
        "dubai uae": "Dubai",
        "dubai united arab emirates": "Dubai",
        "abu dhabi": "Abu Dhabi",
        "abu dhabi uae": "Abu Dhabi",
        "abu dhabi united arab emirates": "Abu Dhabi",
        "auh": "Abu Dhabi",
        "sharjah": "Sharjah",
        "sharjah uae": "Sharjah",
        "sharjah united arab emirates": "Sharjah",
        "ajman": "Ajman",
        "ajman uae": "Ajman",
        "ajman united arab emirates": "Ajman",
    }
    if key not in aliases:
        raise NormalizationError("unsupported_city", "Listing city is outside the supported UAE launch cities")
    return aliases[key]


def normalize_body_type(value: str | None) -> BodyType:
    text = _required(value, "body_type")
    aliases: dict[str, BodyType] = {
        "suv": "SUV",
        "sport utility vehicle": "SUV",
        "sedan": "Sedan",
        "saloon": "Sedan",
        "coupe": "Coupe",
        "hatchback": "Hatchback",
        "pickup": "Pickup",
        "pickup truck": "Pickup",
        "convertible": "Convertible",
        "cabriolet": "Convertible",
    }
    normalized = aliases.get(_alias_key(text))
    if normalized is None:
        raise NormalizationError("unsupported_body_type", "Body type is unsupported")
    return normalized


def normalize_specifications(value: str | None) -> Specifications:
    text = _required(value, "specifications")
    key = _alias_key(text)
    if "gcc" in key or "gulf" in key:
        return "GCC"
    if any(marker in key for marker in ("american", "usa", "us spec")):
        return "American"
    if any(marker in key for marker in ("europe", "euro")):
        return "European"
    if any(marker in key for marker in ("japan", "japanese")):
        return "Japanese"
    raise NormalizationError("unsupported_specifications", "Regional specifications are unsupported")


def normalize_seller_type(value: str | None) -> SellerType:
    text = _required(value, "seller_type")
    key = _alias_key(text)
    if key in {"dealer", "dealership", "showroom"}:
        return "Dealer"
    if key in {"private", "private seller", "owner", "individual"}:
        return "Private"
    raise NormalizationError("unsupported_seller_type", "Seller type is unsupported")


def normalize_condition_evidence(claims: Sequence[RawConditionClaim]) -> list[NormalizedConditionEvidence]:
    if not claims:
        return [
            NormalizedConditionEvidence(
                kind="unknown",
                label="Condition not stated",
                detail="The source did not provide condition evidence.",
            )
        ]
    return [
        NormalizedConditionEvidence(
            kind=claim.kind,
            label=claim.label,
            detail=claim.detail,
            source_claim=claim.source_claim,
            confidence=claim.confidence,
        )
        for claim in claims
    ]


def normalize_photos(raw: RawListing) -> list[NormalizedPhoto]:
    provenance: Literal["fixture", "approved"] = (
        "fixture" if raw.reference.source_key == "carveo-fixture" else "approved"
    )
    normalized: list[NormalizedPhoto] = []
    for photo in raw.photos:
        try:
            parsed = urlsplit(photo.source_url)
            _ = parsed.port
        except ValueError as exc:
            raise NormalizationError("invalid_photo_url", "Photo URL is invalid") from exc
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            raise NormalizationError("invalid_photo_url", "Photo URL is invalid")
        if parsed.username is not None or parsed.password is not None:
            raise NormalizationError("invalid_photo_url", "Photo URL credentials are forbidden")
        normalized.append(
            NormalizedPhoto(
                source_url=photo.source_url,
                provenance=provenance,
                source_media_id=photo.source_media_id,
            )
        )
    return normalized


def _required(value: str | None, field: str) -> str:
    if value is None or not value.strip():
        raise NormalizationError(f"missing_{field}", f"{field.replace('_', ' ').capitalize()} is required")
    return value.strip()


def _alias_key(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def _original_values(raw: RawListing) -> dict[str, str]:
    fields = (
        "body_type",
        "city",
        "currency",
        "description",
        "make",
        "mileage",
        "model",
        "price",
        "seller_type",
        "specifications",
        "title",
        "trim",
        "year",
    )
    return {field: value for field in fields if isinstance((value := getattr(raw, field)), str)}


def _reject(raw: RawListing, code: str, detail: str) -> RejectedListing:
    return RejectedListing(reference=raw.reference, error_code=code[:80], detail=detail[:400])
