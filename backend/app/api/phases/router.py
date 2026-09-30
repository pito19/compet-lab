from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_phase_service
from app.application.phases.use_cases import PhaseService
from app.application.shared.context import ActorContext
from app.domain.phases.entities import Phase, Pool
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(tags=["phases"])


class PhaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    order: int = 1


class PhaseResponse(BaseModel):
    id: uuid.UUID
    competition_id: uuid.UUID | None
    name: str
    order: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, p: Phase) -> "PhaseResponse":
        return cls(
            id=p.id, competition_id=p.competition_id, name=p.name, order=p.order,
            created_at=p.created_at, updated_at=p.updated_at,
        )


class PoolCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class PoolResponse(BaseModel):
    id: uuid.UUID
    phase_id: uuid.UUID | None
    name: str
    team_ids: list[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, p: Pool) -> "PoolResponse":
        return cls(
            id=p.id, phase_id=p.phase_id, name=p.name, team_ids=p.team_ids,
            created_at=p.created_at, updated_at=p.updated_at,
        )


class AddTeamToPoolRequest(BaseModel):
    team_id: uuid.UUID


@router.post(
    "/api/competitions/{competition_id}/phases", response_model=PhaseResponse, status_code=status.HTTP_201_CREATED
)
def create_phase(
    competition_id: uuid.UUID,
    payload: PhaseCreateRequest,
    service: PhaseService = Depends(get_phase_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    phase = service.create_phase(competition_id, payload.name, payload.order)
    return PhaseResponse.from_domain(phase)


@router.get("/api/competitions/{competition_id}/phases", response_model=list[PhaseResponse])
def list_phases(
    competition_id: uuid.UUID,
    service: PhaseService = Depends(get_phase_service),
    actor: ActorContext = Depends(get_current_actor),
):
    return [PhaseResponse.from_domain(p) for p in service.list_phases(competition_id)]


@router.post("/api/phases/{phase_id}/pools", response_model=PoolResponse, status_code=status.HTTP_201_CREATED)
def create_pool(
    phase_id: uuid.UUID,
    payload: PoolCreateRequest,
    service: PhaseService = Depends(get_phase_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    pool = service.create_pool(phase_id, payload.name)
    return PoolResponse.from_domain(pool)


@router.get("/api/phases/{phase_id}/pools", response_model=list[PoolResponse])
def list_pools(
    phase_id: uuid.UUID,
    service: PhaseService = Depends(get_phase_service),
    actor: ActorContext = Depends(get_current_actor),
):
    return [PoolResponse.from_domain(p) for p in service.list_pools(phase_id)]


@router.post("/api/pools/{pool_id}/teams", response_model=PoolResponse)
def add_team_to_pool(
    pool_id: uuid.UUID,
    payload: AddTeamToPoolRequest,
    service: PhaseService = Depends(get_phase_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    pool = service.add_team_to_pool(pool_id, payload.team_id)
    return PoolResponse.from_domain(pool)
