from __future__ import annotations

import uuid

from app.domain.phases.entities import Phase, Pool
from app.domain.shared.exceptions import ConflictError, NotFoundError
from app.domain.shared.ports import (
    CompetitionRepository,
    PhaseRepository,
    PoolRepository,
    TeamRepository,
)


class PhaseService:
    def __init__(
        self,
        phases: PhaseRepository,
        pools: PoolRepository,
        teams: TeamRepository,
        competitions: CompetitionRepository,
    ) -> None:
        self._phases = phases
        self._pools = pools
        self._teams = teams
        self._competitions = competitions

    def create_phase(self, competition_id: uuid.UUID, name: str, order: int) -> Phase:
        competition = self._competitions.get(competition_id)
        if competition is None:
            raise NotFoundError("Competition not found.", {"competition_id": str(competition_id)})
        competition.ensure_editable()
        phase = Phase(competition_id=competition_id, name=name, order=order)
        return self._phases.add(phase)

    def list_phases(self, competition_id: uuid.UUID) -> list[Phase]:
        return self._phases.list_by_competition(competition_id)

    def create_pool(self, phase_id: uuid.UUID, name: str) -> Pool:
        phase = self._phases.get(phase_id)
        if phase is None:
            raise NotFoundError("Phase not found.", {"phase_id": str(phase_id)})
        pool = Pool(phase_id=phase_id, name=name)
        return self._pools.add(pool)

    def list_pools(self, phase_id: uuid.UUID) -> list[Pool]:
        return self._pools.list_by_phase(phase_id)

    def add_team_to_pool(self, pool_id: uuid.UUID, team_id: uuid.UUID) -> Pool:
        pool = self._pools.get(pool_id)
        if pool is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(pool_id)})
        team = self._teams.get(team_id)
        if team is None:
            raise NotFoundError("Team not found.", {"team_id": str(team_id)})

        # Business rule: a team can only be placed in a pool belonging to
        # the competition it is registered in.
        phase = self._phases.get(pool.phase_id) if pool.phase_id else None
        if phase is None or phase.competition_id != team.competition_id:
            raise ConflictError(
                "The team is not registered in the competition this pool belongs to.",
                {"pool_id": str(pool_id), "team_id": str(team_id)},
            )

        pool.add_team(team_id)  # raises ConflictError if already registered

        # Pool.team_ids is derived from teams.pool_id (see SqlPoolRepository),
        # so the team's assignment MUST be persisted before the pool is
        # reloaded -- otherwise the returned pool omits the team just added.
        team.assign_to_pool(pool_id)
        self._teams.update(team)

        updated_pool = self._pools.update(pool)
        return updated_pool
