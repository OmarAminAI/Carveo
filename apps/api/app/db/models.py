from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SearchSessionRecord(Base):
    __tablename__ = "search_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    intent: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    messages: Mapped[list["SearchMessageRecord"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class SearchMessageRecord(Base):
    __tablename__ = "search_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("search_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    session: Mapped[SearchSessionRecord] = relationship(back_populates="messages")


class SavedSearchRecord(Base):
    __tablename__ = "saved_searches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(120))
    query: Mapped[dict] = mapped_column(JSON, default=dict)
    priority_refresh: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceRecord(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    market: Mapped[str] = mapped_column(String(16), index=True)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(24), default="pending_approval")
    access_method: Mapped[str] = mapped_column(String(32), default="crawl4ai")
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=0)
    adapter_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    terms_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PriceObservationRecord(Base):
    __tablename__ = "price_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    listing_id: Mapped[str] = mapped_column(String(96), index=True)
    price: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(8))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
