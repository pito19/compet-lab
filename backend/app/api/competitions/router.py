from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api.competitions.schemas import (
    CompetitionCreateRequest,
    CompetitionListResponse,
    CompetitionRenameRequest,
    CompetitionResponse,
)
from app.api.dependencies import get_competition_service
from app.api.shared.pagination import PageParams
from app.application.competitions.use_cases import CompetitionService, CreateCompetitionInput
from app.application.shared.context import ActorContext
from app.infrastructure.security.auth import get_current_actor, require_manager_or_admin

router = APIRouter(prefix="/api/competitions", tags=["competitions"])


@router.post("", response_model=CompetitionResponse, status_code=status.HTTP_201_CREATED)
def create_competition(
    payload: CompetitionCreateRequest,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    competition = service.create(
        CreateCompetitionInput(
            season_id=payload.season_id,
            name=payload.name,
            category=payload.category,
            gender=payload.gender,
            type=payload.type,
        ),
        actor,
    )
    return CompetitionResponse.from_domain(competition)


@router.get("", response_model=CompetitionListResponse)
def list_competitions(
    page_params: PageParams = Depends(),
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(get_current_actor),
):
    items, total = service.list(limit=page_params.limit, offset=page_params.offset)
    return CompetitionListResponse(
        items=[CompetitionResponse.from_domain(c) for c in items],
        total=total,
        page=page_params.page,
        page_size=page_params.page_size,
    )


@router.get("/{competition_id}", response_model=CompetitionResponse)
def get_competition(
    competition_id: uuid.UUID,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(get_current_actor),
):
    return CompetitionResponse.from_domain(service.get(competition_id))


@router.patch("/{competition_id}", response_model=CompetitionResponse)
def rename_competition(
    competition_id: uuid.UUID,
    payload: CompetitionRenameRequest,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    return CompetitionResponse.from_domain(service.rename(competition_id, payload.name, actor))


@router.post("/{competition_id}/activate", response_model=CompetitionResponse)
def activate_competition(
    competition_id: uuid.UUID,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    return CompetitionResponse.from_domain(service.activate(competition_id, actor))


@router.post("/{competition_id}/close", response_model=CompetitionResponse)
def close_competition(
    competition_id: uuid.UUID,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    return CompetitionResponse.from_domain(service.close(competition_id, actor))


@router.post("/{competition_id}/publish", response_model=CompetitionResponse)
def publish_competition(
    competition_id: uuid.UUID,
    service: CompetitionService = Depends(get_competition_service),
    actor: ActorContext = Depends(require_manager_or_admin),
):
    return CompetitionResponse.from_domain(service.publish(competition_id, actor))
