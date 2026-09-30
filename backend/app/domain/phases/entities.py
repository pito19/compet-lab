from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from app.domain.shared.base import Entity
from app.domain.shared.exceptions import ConflictError


@dataclass
class Phase(Entity):
    competition_id: uuid.UUID | None = None
    name: str = ""
    order: int = 1


@dataclass
class Pool(Entity):
    phase_id: uuid.UUID | None = None
    name: str = ""
    team_ids: list[uuid.UUID] = field(default_factory=list)

    def add_team(self, team_id: uuid.UUID) -> None:
        """Business rule: a team can only be registered once in a pool."""
        if team_id in self.team_ids:
            raise ConflictError(
                "This team is already registered in this pool.",
                {"pool_id": str(self.id), "team_id": str(team_id)},
            )
        self.team_ids.append(team_id)
        self.touch()

    def remove_team(self, team_id: uuid.UUID) -> None:
        if team_id in self.team_ids:
            self.team_ids.remove(team_id)
            self.touch()
