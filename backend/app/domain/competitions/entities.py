from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from app.domain.shared.base import Entity
from app.domain.shared.exceptions import InvalidStateError


class CompetitionStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class CompetitionType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    CUP = "CUP"
    TOURNAMENT = "TOURNAMENT"


@dataclass
class Season(Entity):
    label: str = ""  # e.g. "2026/2027"
    is_current: bool = False


@dataclass
class Competition(Entity):
    season_id: uuid.UUID | None = None
    name: str = ""
    category: str = ""  # e.g. "U15", "Seniors"
    gender: str = "MIXED"
    type: CompetitionType = CompetitionType.CHAMPIONSHIP
    status: CompetitionStatus = CompetitionStatus.DRAFT
    is_published: bool = False

    # legacy interop -- populated only for competitions imported through
    # the Legacy Adapter. None for competitions created natively.
    legacy_id: str | None = None

    def activate(self) -> None:
        if self.status == CompetitionStatus.CLOSED:
            raise InvalidStateError(
                "A closed competition cannot be reactivated.",
                {"competition_id": str(self.id)},
            )
        self.status = CompetitionStatus.ACTIVE
        self.touch()

    def close(self) -> None:
        self.status = CompetitionStatus.CLOSED
        self.is_published = False
        self.touch()

    def publish(self) -> None:
        if self.status != CompetitionStatus.ACTIVE:
            raise InvalidStateError(
                "Only an ACTIVE competition can be published.",
                {"competition_id": str(self.id), "status": self.status.value},
            )
        self.is_published = True
        self.touch()

    def ensure_editable(self) -> None:
        if self.status == CompetitionStatus.CLOSED:
            raise InvalidStateError(
                "A closed competition cannot be modified directly.",
                {"competition_id": str(self.id)},
            )

    def rename(self, name: str) -> None:
        self.ensure_editable()
        self.name = name
        self.touch()
