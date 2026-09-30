from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_scheduling_service
from app.application.scheduling.use_cases import GenerateScheduleInput, SchedulingService
from app.application.shared.context import ActorContext
from app.domain.matches.entities import Match, MatchStatus
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(tags=["matches"])


class GenerateScheduleRequest(BaseModel):
    start_date: datetime
    days_between_matchdays: int = Field(default=7, ge=1, le=60)


class MatchResponse(BaseModel):
    id: uuid.UUID
    pool_id: uuid.UUID | None
    home_team_id: uuid.UUID | None
    away_team_id: uuid.UUID | None
    scheduled_at: datetime | None
    venue_id: uuid.UUID | None
    status: MatchStatus

    @classmethod
    def from_domain(cls, m: Match) -> "MatchResponse":
        return cls(
            id=m.id, pool_id=m.pool_id, home_team_id=m.home_team_id, away_team_id=m.away_team_id,
            scheduled_at=m.scheduled_at, venue_id=m.venue_id, status=m.status,
        )


class RescheduleMatchRequest(BaseModel):
    scheduled_at: datetime
    venue_id: uuid.UUID | None = None


class ConflictResponse(BaseModel):
    type: str
    severity: str
    match_id: uuid.UUID
    message: str


@router.post(
    "/api/pools/{pool_id}/schedule", response_model=list[MatchResponse], status_code=status.HTTP_201_CREATED
)
def generate_schedule(
    pool_id: uuid.UUID,
    payload: GenerateScheduleRequest,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    matches = service.generate(
        GenerateScheduleInput(
            pool_id=pool_id, start_date=payload.start_date, days_between_matchdays=payload.days_between_matchdays
        )
    )
    return [MatchResponse.from_domain(m) for m in matches]


@router.get("/api/pools/{pool_id}/matches", response_model=list[MatchResponse])
def list_pool_matches(
    pool_id: uuid.UUID,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(get_current_actor),
):
    matches = service.list_matches(pool_id)
    return [MatchResponse.from_domain(m) for m in matches]


@router.patch("/api/matches/{match_id}", response_model=MatchResponse)
def reschedule_match(
    match_id: uuid.UUID,
    payload: RescheduleMatchRequest,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    updated = service.reschedule_match(match_id, payload.scheduled_at, payload.venue_id, actor)
    return MatchResponse.from_domain(updated)


@router.post("/api/matches/{match_id}/postpone", response_model=MatchResponse)
def postpone_match(
    match_id: uuid.UUID,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    updated = service.postpone_match(match_id, actor)
    return MatchResponse.from_domain(updated)


@router.post("/api/matches/{match_id}/cancel", response_model=MatchResponse)
def cancel_match(
    match_id: uuid.UUID,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    updated = service.cancel_match(match_id, actor)
    return MatchResponse.from_domain(updated)


@router.get("/api/pools/{pool_id}/quality/conflicts", response_model=list[ConflictResponse])
def get_conflicts(
    pool_id: uuid.UUID,
    service: SchedulingService = Depends(get_scheduling_service),
    actor: ActorContext = Depends(get_current_actor),
):
    conflicts = service.detect_conflicts(pool_id)
    return [
        ConflictResponse(type=c.type, severity=c.severity, match_id=c.match_id, message=c.message)
        for c in conflicts
    ]
