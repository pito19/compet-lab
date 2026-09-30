from __future__ import annotations

import uuid

from app.application.shared.context import ActorContext
from app.domain.audit.entities import AuditEvent
from app.domain.matches.entities import MatchResult, MatchStatus
from app.domain.shared.exceptions import InvalidStateError, NotFoundError
from app.domain.shared.ports import AuditRepository, MatchRepository, MatchResultRepository, PoolRepository


class ResultService:
    def __init__(
        self,
        results: MatchResultRepository,
        matches: MatchRepository,
        audit: AuditRepository,
        pools: PoolRepository,
    ) -> None:
        self._results = results
        self._matches = matches
        self._audit = audit
        self._pools = pools

    def record_result(
        self, match_id: uuid.UUID, home_score: int, away_score: int, actor: ActorContext
    ) -> MatchResult:
        match = self._matches.get(match_id)
        if match is None:
            raise NotFoundError("Match not found.", {"match_id": str(match_id)})
        if match.status == MatchStatus.CANCELLED:
            raise InvalidStateError(
                "Cannot record a result for a cancelled match.", {"match_id": str(match_id)}
            )

        existing = self._results.get_by_match(match_id)
        if existing is not None:
            old = {"home_score": existing.home_score, "away_score": existing.away_score}
            existing.correct(home_score, away_score)
            saved = self._results.update(existing)
            self._audit.add(
                AuditEvent(
                    actor_id=actor.id,
                    actor_email=actor.email,
                    action="RESULT_CORRECTED",
                    entity_type="MatchResult",
                    entity_id=saved.id,
                    old_value=old,
                    new_value={"home_score": home_score, "away_score": away_score},
                )
            )
        else:
            result = MatchResult(match_id=match_id, home_score=home_score, away_score=away_score)
            result.validate()
            saved = self._results.add(result)
            self._audit.add(
                AuditEvent(
                    actor_id=actor.id,
                    actor_email=actor.email,
                    action="RESULT_RECORDED",
                    entity_type="MatchResult",
                    entity_id=saved.id,
                    old_value={},
                    new_value={"home_score": home_score, "away_score": away_score},
                )
            )

        match.mark_played()
        self._matches.update(match)

        return saved

    def list_by_pool(self, pool_id: uuid.UUID) -> list[MatchResult]:
        if self._pools.get(pool_id) is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(pool_id)})
        return self._results.list_by_pool(pool_id)
