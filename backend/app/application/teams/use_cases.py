from __future__ import annotations

import uuid

from app.domain.shared.exceptions import NotFoundError
from app.domain.shared.ports import CompetitionRepository, TeamRepository
from app.domain.teams.entities import Team


class TeamService:
    def __init__(self, repo: TeamRepository, competitions: CompetitionRepository) -> None:
        self._repo = repo
        self._competitions = competitions

    def add_team(self, competition_id: uuid.UUID, name: str, club_name: str) -> Team:
        competition = self._competitions.get(competition_id)
        if competition is None:
            raise NotFoundError("Competition not found.", {"competition_id": str(competition_id)})
        competition.ensure_editable()
        team = Team(competition_id=competition_id, name=name, club_name=club_name)
        return self._repo.add(team)

    def list_for_competition(self, competition_id: uuid.UUID) -> list[Team]:
        return self._repo.list_by_competition(competition_id)
