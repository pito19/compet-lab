from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.shared.base import Entity


@dataclass
class Team(Entity):
    competition_id: uuid.UUID | None = None
    name: str = ""
    club_name: str = ""
    pool_id: uuid.UUID | None = None

    legacy_id: str | None = None

    def assign_to_pool(self, pool_id: uuid.UUID) -> None:
        self.pool_id = pool_id
        self.touch()
