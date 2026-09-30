from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.application.scheduling.round_robin import default_kickoff_times, generate_round_robin_pairings
from app.application.shared.context import ActorContext
from app.domain.audit.entities import AuditEvent
from app.domain.matches.entities import Match, MatchStatus
from app.domain.shared.exceptions import ConflictError, NotFoundError
from app.domain.shared.ports import AuditRepository, MatchRepository, PoolRepository


@dataclass
class GenerateScheduleInput:
    pool_id: uuid.UUID
    start_date: datetime
    days_between_matchdays: int = 7


@dataclass
class ScheduleConflict:
    type: str
    severity: str
    match_id: uuid.UUID
    message: str


class SchedulingService:
    def __init__(self, pools: PoolRepository, matches: MatchRepository, audit: AuditRepository) -> None:
        self._pools = pools
        self._matches = matches
        self._audit = audit

    def generate(self, data: GenerateScheduleInput) -> list[Match]:
        pool = self._pools.get(data.pool_id)
        if pool is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(data.pool_id)})

        if self._matches.has_played_matches(data.pool_id):
            raise ConflictError(
                "Cannot regenerate a schedule for a pool that already has played matches.",
                {"pool_id": str(data.pool_id)},
            )

        # Idempotence rule: wipe unplayed matches before regenerating.
        self._matches.delete_unplayed_by_pool(data.pool_id)

        matchdays = generate_round_robin_pairings(pool.team_ids)
        kickoffs = default_kickoff_times(data.start_date, len(matchdays), data.days_between_matchdays)

        new_matches: list[Match] = []
        for matchday_pairs, kickoff in zip(matchdays, kickoffs):
            for home_id, away_id in matchday_pairs:
                match = Match(
                    pool_id=data.pool_id,
                    home_team_id=home_id,
                    away_team_id=away_id,
                    scheduled_at=kickoff,
                    status=MatchStatus.SCHEDULED,
                )
                new_matches.append(match)

        return self._matches.add_many(new_matches)

    def get_match(self, match_id: uuid.UUID) -> Match:
        match = self._matches.get(match_id)
        if match is None:
            raise NotFoundError("Match not found.", {"match_id": str(match_id)})
        return match

    def list_matches(self, pool_id: uuid.UUID) -> list[Match]:
        if self._pools.get(pool_id) is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(pool_id)})
        return self._matches.list_by_pool(pool_id)

    def reschedule_match(
        self, match_id: uuid.UUID, scheduled_at: datetime, venue_id: uuid.UUID | None, actor: ActorContext
    ) -> Match:
        match = self.get_match(match_id)
        old_value = {"scheduled_at": match.scheduled_at.isoformat() if match.scheduled_at else None, "status": match.status.value}
        match.reschedule(scheduled_at, venue_id)
        updated = self._matches.update(match)
        self._audit.add(
            AuditEvent(
                actor_id=actor.id, actor_email=actor.email, action="MATCH_RESCHEDULED",
                entity_type="Match", entity_id=match.id, old_value=old_value,
                new_value={"scheduled_at": scheduled_at.isoformat(), "status": updated.status.value},
            )
        )
        return updated

    def postpone_match(self, match_id: uuid.UUID, actor: ActorContext) -> Match:
        match = self.get_match(match_id)
        old_status = match.status.value
        match.postpone()
        updated = self._matches.update(match)
        self._audit.add(
            AuditEvent(
                actor_id=actor.id, actor_email=actor.email, action="MATCH_POSTPONED",
                entity_type="Match", entity_id=match.id,
                old_value={"status": old_status}, new_value={"status": updated.status.value},
            )
        )
        return updated

    def cancel_match(self, match_id: uuid.UUID, actor: ActorContext) -> Match:
        match = self.get_match(match_id)
        old_status = match.status.value
        match.cancel()
        updated = self._matches.update(match)
        self._audit.add(
            AuditEvent(
                actor_id=actor.id, actor_email=actor.email, action="MATCH_CANCELLED",
                entity_type="Match", entity_id=match.id,
                old_value={"status": old_status}, new_value={"status": updated.status.value},
            )
        )
        return updated

    def detect_conflicts(self, pool_id: uuid.UUID) -> list[ScheduleConflict]:
        """Deterministic conflict detection (V1 Smart Operations, no
        recommendation engine, no AI): a team cannot play two matches
        on the same calendar day."""
        if self._pools.get(pool_id) is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(pool_id)})

        matches = self._matches.list_by_pool(pool_id)
        conflicts: list[ScheduleConflict] = []

        by_day_team: dict[tuple, list[Match]] = {}
        for m in matches:
            if m.scheduled_at is None or m.status in (MatchStatus.CANCELLED,):
                continue
            day = m.scheduled_at.date()
            for team_id in (m.home_team_id, m.away_team_id):
                key = (day, team_id)
                by_day_team.setdefault(key, []).append(m)

        seen_match_pairs: set[tuple[uuid.UUID, uuid.UUID]] = set()
        for (day, team_id), day_matches in by_day_team.items():
            if len(day_matches) > 1:
                for m in day_matches:
                    pair_key = (day, m.id)
                    if pair_key in seen_match_pairs:
                        continue
                    seen_match_pairs.add(pair_key)
                    conflicts.append(
                        ScheduleConflict(
                            type="TEAM_DOUBLE_BOOKED",
                            severity="HIGH",
                            match_id=m.id,
                            message=(
                                f"Team {team_id} is scheduled for more than one match on {day.isoformat()}."
                            ),
                        )
                    )

        return conflicts
