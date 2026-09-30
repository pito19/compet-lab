from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_team_service
from app.application.shared.context import ActorContext
from app.application.teams.use_cases import TeamService
from app.domain.teams.entities import Team
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(prefix="/api/competitions/{competition_id}/teams", tags=["teams"])


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    club_name: str = Field(default="", max_length=200)


class TeamResponse(BaseModel):
    id: uuid.UUID
    competition_id: uuid.UUID | None
    name: str
    club_name: str
    pool_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, t: Team) -> "TeamResponse":
        return cls(
            id=t.id, competition_id=t.competition_id, name=t.name, club_name=t.club_name,
            pool_id=t.pool_id, created_at=t.created_at, updated_at=t.updated_at,
        )


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def add_team(
    competition_id: uuid.UUID,
    payload: TeamCreateRequest,
    service: TeamService = Depends(get_team_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    team = service.add_team(competition_id, payload.name, payload.club_name)
    return TeamResponse.from_domain(team)


@router.get("", response_model=list[TeamResponse])
def list_teams(
    competition_id: uuid.UUID,
    service: TeamService = Depends(get_team_service),
    actor: ActorContext = Depends(get_current_actor),
):
    teams = service.list_for_competition(competition_id)
    return [TeamResponse.from_domain(t) for t in teams]
