"""This test demonstrates the payoff of the ports/adapters architecture:
RankingService depends only on Protocols (see domain/shared/ports.py),
so it can be tested with simple in-memory fakes -- no SQLAlchemy, no
PostgreSQL, no FastAPI involved at all.
"""
from app.application.rankings.use_cases import RankingService
from app.domain.matches.entities import Match, MatchStatus
from app.domain.phases.entities import Pool
from app.domain.teams.entities import Team


class FakePoolRepository:
    def __init__(self, pool: Pool) -> None:
        self._pool = pool

    def get(self, pool_id):
        return self._pool if pool_id == self._pool.id else None


class FakeTeamRepository:
    def __init__(self, teams: list[Team]) -> None:
        self._teams = {t.id: t for t in teams}

    def get(self, team_id):
        return self._teams.get(team_id)


class FakeMatchRepository:
    def __init__(self, matches: list[Match]) -> None:
        self._matches = matches

    def list_by_pool(self, pool_id):
        return [m for m in self._matches if m.pool_id == pool_id]


class FakeMatchResultRepository:
    def __init__(self, results) -> None:
        self._results = results

    def list_by_pool(self, pool_id):
        return self._results


def _validated_result(match_id, home_score, away_score):
    from app.domain.matches.entities import MatchResult

    result = MatchResult(match_id=match_id, home_score=home_score, away_score=away_score)
    result.validate()
    return result


def test_ranking_service_computes_standings_from_fakes_without_any_database():
    team_a, team_b, team_c = Team(name="Alpha"), Team(name="Bravo"), Team(name="Charlie")
    pool = Pool(name="Poule A", team_ids=[team_a.id, team_b.id, team_c.id])

    match_ab = Match(pool_id=pool.id, home_team_id=team_a.id, away_team_id=team_b.id, status=MatchStatus.PLAYED)
    match_bc = Match(pool_id=pool.id, home_team_id=team_b.id, away_team_id=team_c.id, status=MatchStatus.PLAYED)

    results = [
        _validated_result(match_ab.id, home_score=3, away_score=1),  # Alpha beats Bravo
        _validated_result(match_bc.id, home_score=2, away_score=2),  # Bravo draws Charlie
    ]

    service = RankingService(
        pools=FakePoolRepository(pool),
        teams=FakeTeamRepository([team_a, team_b, team_c]),
        matches=FakeMatchRepository([match_ab, match_bc]),
        results=FakeMatchResultRepository(results),
    )

    standings = service.compute_standings(pool.id)
    by_name = {s.team_name: s for s in standings}

    assert by_name["Alpha"].points == 3
    assert by_name["Bravo"].points == 1  # 1 loss + 1 draw
    assert by_name["Charlie"].points == 1
    assert standings[0].team_name == "Alpha"  # ranked first on points
