from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_result_service
from app.application.results.use_cases import ResultService
from app.application.shared.context import ActorContext
from app.domain.matches.entities import MatchResult
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(tags=["results"])


class RecordResultRequest(BaseModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class MatchResultResponse(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID | None
    home_score: int
    away_score: int
    is_validated: bool
    correction_count: int
    updated_at: datetime

    @classmethod
    def from_domain(cls, r: MatchResult) -> "MatchResultResponse":
        return cls(
            id=r.id, match_id=r.match_id, home_score=r.home_score, away_score=r.away_score,
            is_validated=r.is_validated, correction_count=r.correction_count, updated_at=r.updated_at,
        )


@router.post("/api/matches/{match_id}/result", response_model=MatchResultResponse)
def record_result(
    match_id: uuid.UUID,
    payload: RecordResultRequest,
    service: ResultService = Depends(get_result_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    result = service.record_result(match_id, payload.home_score, payload.away_score, actor)
    return MatchResultResponse.from_domain(result)


@router.get("/api/pools/{pool_id}/results", response_model=list[MatchResultResponse])
def list_pool_results(
    pool_id: uuid.UUID,
    service: ResultService = Depends(get_result_service),
    actor: ActorContext = Depends(get_current_actor),
):
    results = service.list_by_pool(pool_id)
    return [MatchResultResponse.from_domain(r) for r in results]
