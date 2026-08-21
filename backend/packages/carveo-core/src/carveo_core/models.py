from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
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


class BuyerProfileRecord(Base, TimestampMixin):
    __tablename__ = "buyer_profiles"
    __table_args__ = (Index("ix_buyer_profiles_clerk_user_id", "clerk_user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    anonymous_merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    shortlist_items: Mapped[list[BuyerShortlistItemRecord]] = relationship(
        back_populates="buyer_profile", cascade="all, delete-orphan"
    )
    comparison_items: Mapped[list[BuyerComparisonItemRecord]] = relationship(
        back_populates="buyer_profile", cascade="all, delete-orphan"
    )
    saved_searches: Mapped[list[BuyerSavedSearchRecord]] = relationship(
        back_populates="buyer_profile", cascade="all, delete-orphan"
    )
    conversations: Mapped[list[BuyerConversationRecord]] = relationship(
        back_populates="buyer_profile", cascade="all, delete-orphan"
    )


class BuyerShortlistItemRecord(Base):
    __tablename__ = "buyer_shortlist_items"
    __table_args__ = (
        UniqueConstraint("buyer_profile_id", "listing_id", name="uq_buyer_shortlist_items_profile_listing"),
        Index("ix_buyer_shortlist_items_buyer_profile_id", "buyer_profile_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buyer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    buyer_profile: Mapped[BuyerProfileRecord] = relationship(back_populates="shortlist_items")


class BuyerComparisonItemRecord(Base):
    __tablename__ = "buyer_comparison_items"
    __table_args__ = (
        UniqueConstraint("buyer_profile_id", "listing_id", name="uq_buyer_comparison_items_profile_listing"),
        UniqueConstraint("buyer_profile_id", "position", name="uq_buyer_comparison_items_profile_position"),
        CheckConstraint("position BETWEEN 0 AND 3", name="ck_buyer_comparison_items_position"),
        Index("ix_buyer_comparison_items_buyer_profile_id", "buyer_profile_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buyer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("listings.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    buyer_profile: Mapped[BuyerProfileRecord] = relationship(back_populates="comparison_items")


class BuyerSavedSearchRecord(Base, TimestampMixin):
    __tablename__ = "buyer_saved_searches"
    __table_args__ = (
        UniqueConstraint("buyer_profile_id", "query", name="uq_buyer_saved_searches_profile_query"),
        Index("ix_buyer_saved_searches_buyer_profile_id", "buyer_profile_id"),
        Index("ix_buyer_saved_searches_profile_updated_at", "buyer_profile_id", "updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buyer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    query: Mapped[str] = mapped_column(String(2000), nullable=False)
    buyer_profile: Mapped[BuyerProfileRecord] = relationship(back_populates="saved_searches")


class BuyerConversationRecord(Base, TimestampMixin):
    __tablename__ = "buyer_conversations"
    __table_args__ = (
        UniqueConstraint("buyer_profile_id", "client_id", name="uq_buyer_conversations_profile_client_id"),
        CheckConstraint("status IN ('active', 'archived')", name="ck_buyer_conversations_status"),
        Index("ix_buyer_conversations_buyer_profile_id", "buyer_profile_id"),
        Index("ix_buyer_conversations_profile_updated_at", "buyer_profile_id", "updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buyer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    interpreted_intent: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    buyer_profile: Mapped[BuyerProfileRecord] = relationship(back_populates="conversations")
    turns: Mapped[list[BuyerConversationTurnRecord]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="BuyerConversationTurnRecord.sequence"
    )


class BuyerConversationTurnRecord(Base):
    __tablename__ = "buyer_conversation_turns"
    __table_args__ = (
        UniqueConstraint("conversation_id", "sequence", name="uq_buyer_conversation_turns_conversation_sequence"),
        CheckConstraint("sequence >= 0", name="ck_buyer_conversation_turns_sequence"),
        CheckConstraint("role IN ('buyer', 'assistant')", name="ck_buyer_conversation_turns_role"),
        Index("ix_buyer_conversation_turns_conversation_id", "conversation_id"),
        Index("ix_buyer_conversation_turns_conversation_sequence", "conversation_id", "sequence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buyer_conversations.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(String(8000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    conversation: Mapped[BuyerConversationRecord] = relationship(back_populates="turns")
