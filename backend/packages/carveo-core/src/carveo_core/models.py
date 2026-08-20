from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Source(Base, TimestampMixin):
    __tablename__ = "sources"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    market: Mapped[str] = mapped_column(String(8), nullable=False)
    authorization_status: Mapped[str] = mapped_column(String(32), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    terms_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    adapter_version: Mapped[str | None] = mapped_column(String(40))
    rate_limit_metadata: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    listings: Mapped[list[ListingRecord]] = relationship(back_populates="source")


class ListingRecord(Base, TimestampMixin):
    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("source_id", "source_listing_id", name="uq_listing_source_identity"),
        Index("ix_listings_market_status_freshness", "market", "lifecycle_status", "last_seen_at"),
        Index("ix_listings_make_model_year", "make", "model", "year"),
        Index("ix_listings_price", "price"),
        Index("ix_listings_mileage", "mileage_km"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_listing_id: Mapped[str] = mapped_column(String(160), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    market: Mapped[str] = mapped_column(String(8), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(24), default="active", nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    trim: Mapped[str] = mapped_column(String(120), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    mileage_km: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    body_type: Mapped[str] = mapped_column(String(48), nullable=False)
    specifications: Mapped[str] = mapped_column(String(48), nullable=False)
    seller_type: Mapped[str] = mapped_column(String(48), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    searchable_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Source] = relationship(back_populates="listings")
    photos: Mapped[list[ListingPhoto]] = relationship(
        back_populates="listing", cascade="all, delete-orphan", order_by="ListingPhoto.position"
    )
    condition_evidence: Mapped[list[ConditionEvidenceRecord]] = relationship(
        back_populates="listing", cascade="all, delete-orphan"
    )
    price_observations: Mapped[list[PriceObservationRecord]] = relationship(
        back_populates="listing", cascade="all, delete-orphan", order_by="PriceObservationRecord.observed_at"
    )
    duplicate_offers: Mapped[list[DuplicateOfferRecord]] = relationship(
        back_populates="listing", cascade="all, delete-orphan"
    )


class ListingPhoto(Base):
    __tablename__ = "listing_photos"
    __table_args__ = (UniqueConstraint("listing_id", "position", name="uq_photo_position"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(String(80), nullable=False)
    source_media_id: Mapped[str | None] = mapped_column(String(160))
    listing: Mapped[ListingRecord] = relationship(back_populates="photos")


class ConditionEvidenceRecord(Base):
    __tablename__ = "condition_evidence"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    source_claim: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    listing: Mapped[ListingRecord] = relationship(back_populates="condition_evidence")


class PriceObservationRecord(Base):
    __tablename__ = "price_observations"
    __table_args__ = (UniqueConstraint("listing_id", "observed_at", name="uq_price_observation_time"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    listing: Mapped[ListingRecord] = relationship(back_populates="price_observations")


class DuplicateOfferRecord(Base):
    __tablename__ = "duplicate_offers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(160), nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    listing: Mapped[ListingRecord] = relationship(back_populates="duplicate_offers")
