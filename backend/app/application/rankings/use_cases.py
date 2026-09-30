from __future__ import annotations

import uuid

from app.domain.rankings.entities import Standing, sort_key
from app.domain.shared.exceptions import NotFoundError
from app.domain.shared.ports import MatchRepository, MatchResultRepository, PoolRepository, TeamRepository


class RankingService:
    """The classement is always computed on the fly from validated
    results -- it is never persisted as an editable table. This is a
    deliberate architectural decision (see domain/rankings/entities.py).
    """

    def __init__(
        self,
        pools: PoolRepository,
        teams: TeamRepository,
        matches: MatchRepository,
        results: MatchResultRepository,
    ) -> None:
        self._pools = pools
        self._teams = teams
        self._matches = matches
        self._results = results

    def compute_standings(self, pool_id: uuid.UUID) -> list[Standing]:
        pool = self._pools.get(pool_id)
        if pool is None:
            raise NotFoundError("Pool not found.", {"pool_id": str(pool_id)})

        all_teams = []
        for team_id in pool.team_ids:
            team = self._teams.get(team_id)
            if team is not None:
                all_teams.append(team)

        standings: dict[uuid.UUID, Standing] = {
            team.id: Standing(team_id=team.id, team_name=team.name) for team in all_teams
        }

        matches = {m.id: m for m in self._matches.list_by_pool(pool_id)}
        results = self._results.list_by_pool(pool_id)

        for result in results:
            if not result.is_validated:
                continue
            match = matches.get(result.match_id)
            if match is None:
                continue

            home = standings.get(match.home_team_id)
            away = standings.get(match.away_team_id)
            if home is None or away is None:
                continue

            home.played += 1
            away.played += 1
            home.goals_for += result.home_score
            home.goals_against += result.away_score
            away.goals_for += result.away_score
            away.goals_against += result.home_score

            if result.home_score > result.away_score:
                home.wins += 1
                away.losses += 1
            elif result.home_score < result.away_score:
                away.wins += 1
                home.losses += 1
            else:
                home.draws += 1
                away.draws += 1

        return sorted(standings.values(), key=sort_key)
