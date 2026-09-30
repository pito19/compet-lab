from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_ranking_service
from app.application.rankings.use_cases import RankingService
from app.application.shared.context import ActorContext
from app.domain.rankings.entities import Standing
from app.infrastructure.security.auth import get_current_actor

router = APIRouter(tags=["rankings"])


class StandingResponse(BaseModel):
    team_id: uuid.UUID
    team_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

    @classmethod
    def from_domain(cls, s: Standing) -> "StandingResponse":
        return cls(
            team_id=s.team_id, team_name=s.team_name, played=s.played, wins=s.wins,
            draws=s.draws, losses=s.losses, goals_for=s.goals_for, goals_against=s.goals_against,
            goal_difference=s.goal_difference, points=s.points,
        )


@router.get("/api/pools/{pool_id}/standings", response_model=list[StandingResponse])
def get_standings(
    pool_id: uuid.UUID,
    service: RankingService = Depends(get_ranking_service),
    actor: ActorContext = Depends(get_current_actor),
):
    standings = service.compute_standings(pool_id)
    return [StandingResponse.from_domain(s) for s in standings]
