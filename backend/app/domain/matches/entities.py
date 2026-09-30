from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.domain.shared.base import Entity
from app.domain.shared.exceptions import InvalidStateError, ValidationError


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    PLAYED = "PLAYED"


@dataclass
class Match(Entity):
    competition_id: uuid.UUID | None = None
    pool_id: uuid.UUID | None = None
    home_team_id: uuid.UUID | None = None
    away_team_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    venue_id: uuid.UUID | None = None
    status: MatchStatus = MatchStatus.SCHEDULED

    legacy_id: str | None = None

    def __post_init__(self) -> None:
        if (
            self.home_team_id is not None
            and self.away_team_id is not None
            and self.home_team_id == self.away_team_id
        ):
            raise ValidationError("A match cannot oppose a team to itself.")

    def reschedule(self, scheduled_at: datetime, venue_id: uuid.UUID | None = None) -> None:
        if self.status == MatchStatus.PLAYED:
            raise InvalidStateError(
                "A played match cannot be rescheduled.",
                {"match_id": str(self.id)},
            )
        self.scheduled_at = scheduled_at
        if venue_id is not None:
            self.venue_id = venue_id
        self.status = MatchStatus.SCHEDULED
        self.touch()

    def postpone(self) -> None:
        if self.status == MatchStatus.PLAYED:
            raise InvalidStateError("A played match cannot be postponed.")
        self.status = MatchStatus.POSTPONED
        self.touch()

    def cancel(self) -> None:
        if self.status == MatchStatus.PLAYED:
            raise InvalidStateError("A played match cannot be cancelled.")
        self.status = MatchStatus.CANCELLED
        self.touch()

    def mark_played(self) -> None:
        self.status = MatchStatus.PLAYED
        self.touch()


@dataclass
class MatchResult(Entity):
    match_id: uuid.UUID | None = None
    home_score: int = 0
    away_score: int = 0
    is_validated: bool = False
    correction_count: int = 0

    def validate(self) -> None:
        if self.home_score < 0 or self.away_score < 0:
            raise ValidationError("Scores cannot be negative.")
        self.is_validated = True
        self.touch()

    def correct(self, home_score: int, away_score: int) -> None:
        """Correcting a validated result is allowed but must always be
        audited by the application layer -- see AuditEvent."""
        if home_score < 0 or away_score < 0:
            raise ValidationError("Scores cannot be negative.")
        self.home_score = home_score
        self.away_score = away_score
        self.correction_count += 1
        self.touch()
