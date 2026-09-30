from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_audit_repository
from app.api.shared.pagination import PageParams
from app.application.shared.context import ActorContext
from app.domain.audit.entities import AuditEvent
from app.infrastructure.security.auth import require_admin

router = APIRouter(tags=["audit"])


class AuditEventResponse(BaseModel):
    id: uuid.UUID
    actor_email: str
    action: str
    entity_type: str
    entity_id: uuid.UUID | None
    old_value: dict
    new_value: dict
    occurred_at: datetime

    @classmethod
    def from_domain(cls, e: AuditEvent) -> "AuditEventResponse":
        return cls(
            id=e.id, actor_email=e.actor_email, action=e.action, entity_type=e.entity_type,
            entity_id=e.entity_id, old_value=e.old_value, new_value=e.new_value, occurred_at=e.occurred_at,
        )


class AuditListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    page: int
    page_size: int


@router.get("/api/audit", response_model=AuditListResponse)
def list_audit_events(
    page_params: PageParams = Depends(),
    repo=Depends(get_audit_repository),
    actor: ActorContext = Depends(require_admin),
):
    items, total = repo.list_all(limit=page_params.limit, offset=page_params.offset)
    return AuditListResponse(
        items=[AuditEventResponse.from_domain(e) for e in items],
        total=total, page=page_params.page, page_size=page_params.page_size,
    )


@router.get("/api/competitions/{competition_id}/audit", response_model=list[AuditEventResponse])
def list_competition_audit_events(
    competition_id: uuid.UUID,
    repo=Depends(get_audit_repository),
    actor: ActorContext = Depends(require_admin),
):
    events = repo.list_by_entity("Competition", competition_id)
    return [AuditEventResponse.from_domain(e) for e in events]
