from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.audit.entities import AuditEvent
from app.domain.competitions.entities import Competition, CompetitionStatus, CompetitionType
from app.domain.shared.exceptions import NotFoundError
from app.domain.shared.ports import AuditRepository, CompetitionRepository
from app.application.shared.context import ActorContext as CurrentUser


@dataclass
class CreateCompetitionInput:
    season_id: uuid.UUID
    name: str
    category: str
    gender: str
    type: CompetitionType


class CompetitionService:
    """Application service orchestrating the Competition use cases.

    Depends only on ports (Protocols), never on concrete infrastructure.
    """

    def __init__(self, repo: CompetitionRepository, audit: AuditRepository) -> None:
        self._repo = repo
        self._audit = audit

    def create(self, data: CreateCompetitionInput, actor: CurrentUser) -> Competition:
        competition = Competition(
            season_id=data.season_id,
            name=data.name,
            category=data.category,
            gender=data.gender,
            type=data.type,
            status=CompetitionStatus.DRAFT,
        )
        created = self._repo.add(competition)
        self._audit.add(_audit_event(actor, "COMPETITION_CREATED", "Competition", created.id, {}, {"name": created.name}))
        return created

    def get(self, competition_id: uuid.UUID) -> Competition:
        competition = self._repo.get(competition_id)
        if competition is None:
            raise NotFoundError("Competition not found.", {"competition_id": str(competition_id)})
        return competition

    def list(self, limit: int, offset: int) -> tuple[list[Competition], int]:
        return self._repo.list(limit=limit, offset=offset)

    def rename(self, competition_id: uuid.UUID, name: str, actor: CurrentUser) -> Competition:
        competition = self.get(competition_id)
        old_name = competition.name
        competition.rename(name)
        updated = self._repo.update(competition)
        self._audit.add(
            _audit_event(actor, "COMPETITION_RENAMED", "Competition", competition.id, {"name": old_name}, {"name": name})
        )
        return updated

    def activate(self, competition_id: uuid.UUID, actor: CurrentUser) -> Competition:
        competition = self.get(competition_id)
        old_status = competition.status.value
        competition.activate()
        updated = self._repo.update(competition)
        self._audit.add(
            _audit_event(
                actor, "COMPETITION_STATUS_CHANGED", "Competition", competition.id,
                {"status": old_status}, {"status": competition.status.value},
            )
        )
        return updated

    def close(self, competition_id: uuid.UUID, actor: CurrentUser) -> Competition:
        competition = self.get(competition_id)
        old_status = competition.status.value
        competition.close()
        updated = self._repo.update(competition)
        self._audit.add(
            _audit_event(
                actor, "COMPETITION_STATUS_CHANGED", "Competition", competition.id,
                {"status": old_status}, {"status": competition.status.value},
            )
        )
        return updated

    def publish(self, competition_id: uuid.UUID, actor: CurrentUser) -> Competition:
        competition = self.get(competition_id)
        competition.publish()
        updated = self._repo.update(competition)
        self._audit.add(
            _audit_event(actor, "COMPETITION_PUBLISHED", "Competition", competition.id, {}, {"is_published": True})
        )
        return updated


def _audit_event(actor: CurrentUser, action: str, entity_type: str, entity_id: uuid.UUID, old: dict, new: dict):
    return AuditEvent(
        actor_id=actor.id,
        actor_email=actor.email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old,
        new_value=new,
    )
