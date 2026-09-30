from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.competitions.use_cases import CompetitionService
from app.application.phases.use_cases import PhaseService
from app.application.rankings.use_cases import RankingService
from app.application.results.use_cases import ResultService
from app.application.scheduling.use_cases import SchedulingService
from app.application.teams.use_cases import TeamService
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import (
    SqlAuditRepository,
    SqlCompetitionRepository,
    SqlMatchRepository,
    SqlMatchResultRepository,
    SqlPhaseRepository,
    SqlPoolRepository,
    SqlTeamRepository,
)


def get_competition_service(db: Session = Depends(get_db)) -> CompetitionService:
    return CompetitionService(SqlCompetitionRepository(db), SqlAuditRepository(db))


def get_team_service(db: Session = Depends(get_db)) -> TeamService:
    return TeamService(SqlTeamRepository(db), SqlCompetitionRepository(db))


def get_phase_service(db: Session = Depends(get_db)) -> PhaseService:
    return PhaseService(
        SqlPhaseRepository(db), SqlPoolRepository(db), SqlTeamRepository(db), SqlCompetitionRepository(db)
    )


def get_scheduling_service(db: Session = Depends(get_db)) -> SchedulingService:
    return SchedulingService(SqlPoolRepository(db), SqlMatchRepository(db), SqlAuditRepository(db))


def get_result_service(db: Session = Depends(get_db)) -> ResultService:
    return ResultService(SqlMatchResultRepository(db), SqlMatchRepository(db), SqlAuditRepository(db), SqlPoolRepository(db))


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    return RankingService(
        SqlPoolRepository(db), SqlTeamRepository(db), SqlMatchRepository(db), SqlMatchResultRepository(db)
    )


def get_audit_repository(db: Session = Depends(get_db)) -> SqlAuditRepository:
    return SqlAuditRepository(db)
