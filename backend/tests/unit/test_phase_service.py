"""PhaseService tested with in-memory fakes -- no database, no framework."""
import uuid

import pytest

from app.application.phases.use_cases import PhaseService
from app.domain.competitions.entities import Competition
from app.domain.phases.entities import Phase, Pool
from app.domain.shared.exceptions import ConflictError, InvalidStateError
from app.domain.teams.entities import Team


class _Repo:
    """Minimal generic in-memory repository."""

    def __init__(self, *items) -> None:
        self.items = {i.id: i for i in items}

    def get(self, item_id):
        return self.items.get(item_id)

    def add(self, item):
        self.items[item.id] = item
        return item

    def update(self, item):
        self.items[item.id] = item
        return item


def _service(competition, phase, pool, *teams):
    return PhaseService(
        phases=_Repo(phase),
        pools=_Repo(pool),
        teams=_Repo(*teams),
        competitions=_Repo(competition),
    )


def _fixture():
    competition = Competition(name="U15")
    phase = Phase(competition_id=competition.id, name="Regular", order=1)
    pool = Pool(phase_id=phase.id, name="A")
    return competition, phase, pool


def test_team_of_same_competition_can_join_pool():
    competition, phase, pool = _fixture()
    team = Team(competition_id=competition.id, name="Alpha")
    service = _service(competition, phase, pool, team)

    updated = service.add_team_to_pool(pool.id, team.id)

    assert team.id in updated.team_ids
    assert team.pool_id == pool.id


def test_added_team_is_present_in_the_returned_pool_even_with_a_repository_that_reloads_from_source():
    """Regression test for a subtle ordering bug: Pool.team_ids is
    derived from teams.pool_id by SqlPoolRepository, so persisting the
    team's assignment must happen BEFORE the pool is reloaded, or the
    just-added team is silently missing from the response."""

    class ReloadingPoolRepo(_Repo):
        """Simulates SqlPoolRepository.update(): ignores the in-memory
        pool passed in and recomputes team_ids from the team repo."""

        def __init__(self, pool: Pool, team_repo: "_Repo") -> None:
            super().__init__(pool)
            self._team_repo = team_repo

        def update(self, pool: Pool) -> Pool:
            recomputed = Pool(
                id=pool.id, phase_id=pool.phase_id, name=pool.name,
                team_ids=[t.id for t in self._team_repo.items.values() if t.pool_id == pool.id],
            )
            self.items[pool.id] = recomputed
            return recomputed

    competition, phase, pool = _fixture()
    team = Team(competition_id=competition.id, name="Alpha")
    team_repo = _Repo(team)
    service = PhaseService(
        phases=_Repo(phase),
        pools=ReloadingPoolRepo(pool, team_repo),
        teams=team_repo,
        competitions=_Repo(competition),
    )

    updated = service.add_team_to_pool(pool.id, team.id)

    assert team.id in updated.team_ids


def test_team_of_another_competition_is_rejected():
    competition, phase, pool = _fixture()
    foreign_team = Team(competition_id=uuid.uuid4(), name="Foreign")
    service = _service(competition, phase, pool, foreign_team)

    with pytest.raises(ConflictError):
        service.add_team_to_pool(pool.id, foreign_team.id)
    assert foreign_team.pool_id is None


def test_cannot_create_phase_on_closed_competition():
    competition, phase, pool = _fixture()
    competition.close()
    service = _service(competition, phase, pool)

    with pytest.raises(InvalidStateError):
        service.create_phase(competition.id, "Playoffs", 2)
