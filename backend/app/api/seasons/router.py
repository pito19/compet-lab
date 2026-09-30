from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.shared.context import ActorContext
from app.domain.competitions.entities import Season
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import SqlSeasonRepository
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(prefix="/api/seasons", tags=["seasons"])


class SeasonCreateRequest(BaseModel):
    label: str = Field(min_length=2, max_length=50)
    is_current: bool = False


class SeasonResponse(BaseModel):
    id: uuid.UUID
    label: str
    is_current: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, s: Season) -> "SeasonResponse":
        return cls(id=s.id, label=s.label, is_current=s.is_current, created_at=s.created_at, updated_at=s.updated_at)


@router.get("", response_model=list[SeasonResponse])
def list_seasons(db: Session = Depends(get_db), actor: ActorContext = Depends(get_current_actor)):
    seasons = SqlSeasonRepository(db).list()
    return [SeasonResponse.from_domain(s) for s in seasons]


@router.post("", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
def create_season(
    payload: SeasonCreateRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    season = SqlSeasonRepository(db).add(Season(label=payload.label, is_current=payload.is_current))
    return SeasonResponse.from_domain(season)
