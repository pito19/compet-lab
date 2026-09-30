from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.rankings.router import StandingResponse
from app.api.shared.pagination import PageParams
from app.application.rankings.use_cases import RankingService
from app.domain.competitions.entities import CompetitionStatus
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlCompetitionRepository,
    SqlMatchRepository,
    SqlMatchResultRepository,
    SqlPhaseRepository,
    SqlPoolRepository,
    SqlTeamRepository,
)

# Deliberately separate router, own prefix, NO auth dependency: this is
# the "consumer-facing" read-only surface referenced in the Legacy /
# modernization narrative (API publique vs API de gestion).
router = APIRouter(prefix="/api/public", tags=["public"])


class PublicCompetitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    gender: str
    updated_at: datetime


def _require_pool_of_published_competition(pool_id: uuid.UUID, db: Session) -> None:
    """Guard used by every /public endpoint keyed by pool_id: walks
    pool -> phase -> competition and rejects anything that is not a
    published, active competition. Without this check, a pool_id from
    a DRAFT/unpublished competition would leak through the public,
    unauthenticated surface -- which would defeat the purpose of the
    is_published flag entirely.
    """
    pool = SqlPoolRepository(db).get(pool_id)
    if pool is None or pool.phase_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found.")

    phase = SqlPhaseRepository(db).get(pool.phase_id)
    if phase is None or phase.competition_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found.")

    competition = SqlCompetitionRepository(db).get(phase.competition_id)
    if competition is None or not competition.is_published or competition.status != CompetitionStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found.")


class PublicCompetitionListResponse(BaseModel):
    items: list[PublicCompetitionResponse]
    total: int
    page: int
    page_size: int


@router.get("/competitions", response_model=PublicCompetitionListResponse)
def list_published_competitions(page_params: PageParams = Depends(), db: Session = Depends(get_db)):
    items, total = SqlCompetitionRepository(db).list_published(limit=page_params.limit, offset=page_params.offset)
    return PublicCompetitionListResponse(
        items=[
            PublicCompetitionResponse(id=c.id, name=c.name, category=c.category, gender=c.gender, updated_at=c.updated_at)
            for c in items
        ],
        total=total,
        page=page_params.page,
        page_size=page_params.page_size,
    )


@router.get("/pools/{pool_id}/standings", response_model=list[StandingResponse])
def public_standings(pool_id: uuid.UUID, db: Session = Depends(get_db)):
    _require_pool_of_published_competition(pool_id, db)

    service = RankingService(
        SqlPoolRepository(db), SqlTeamRepository(db), SqlMatchRepository(db), SqlMatchResultRepository(db)
    )
    standings = service.compute_standings(pool_id)
    return [StandingResponse.from_domain(s) for s in standings]
