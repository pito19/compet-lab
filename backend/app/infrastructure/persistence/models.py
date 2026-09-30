from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base


def _uuid_col(**kwargs):
    return mapped_column(PG_UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, **kwargs)


class SeasonModel(Base):
    __tablename__ = "seasons"

    id: Mapped[uuid.UUID] = _uuid_col()
    label: Mapped[str] = mapped_column(String(50))
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CompetitionModel(Base):
    __tablename__ = "competitions"

    id: Mapped[uuid.UUID] = _uuid_col()
    season_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("seasons.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), default="")
    gender: Mapped[str] = mapped_column(String(20), default="MIXED")
    type: Mapped[str] = mapped_column(String(20), default="CHAMPIONSHIP")
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    legacy_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    teams: Mapped[list["TeamModel"]] = relationship(back_populates="competition")
    phases: Mapped[list["PhaseModel"]] = relationship(back_populates="competition")


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = _uuid_col()
    competition_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("competitions.id"))
    name: Mapped[str] = mapped_column(String(200))
    club_name: Mapped[str] = mapped_column(String(200), default="")
    pool_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("pools.id"), nullable=True)
    legacy_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    competition: Mapped["CompetitionModel"] = relationship(back_populates="teams")


class PhaseModel(Base):
    __tablename__ = "phases"

    id: Mapped[uuid.UUID] = _uuid_col()
    competition_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("competitions.id"))
    name: Mapped[str] = mapped_column(String(200))
    order: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    competition: Mapped["CompetitionModel"] = relationship(back_populates="phases")
    pools: Mapped[list["PoolModel"]] = relationship(back_populates="phase")


class PoolModel(Base):
    __tablename__ = "pools"

    id: Mapped[uuid.UUID] = _uuid_col()
    phase_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("phases.id"))
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    phase: Mapped["PhaseModel"] = relationship(back_populates="pools")


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = _uuid_col()
    pool_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("pools.id"))
    home_team_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("teams.id"))
    away_team_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("teams.id"))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    venue_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED")
    legacy_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MatchResultModel(Base):
    __tablename__ = "match_results"

    id: Mapped[uuid.UUID] = _uuid_col()
    match_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("matches.id"), unique=True)
    home_score: Mapped[int] = mapped_column(Integer, default=0)
    away_score: Mapped[int] = mapped_column(Integer, default=0)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    correction_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_col()
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    full_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(20), default="VIEWER")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = _uuid_col()
    actor_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    actor_email: Mapped[str] = mapped_column(String(200), default="")
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    old_value: Mapped[dict] = mapped_column(JSON, default=dict)
    new_value: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
