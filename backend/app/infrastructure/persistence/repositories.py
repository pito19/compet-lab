from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.audit.entities import AuditEvent
from app.domain.competitions.entities import Competition, Season
from app.domain.matches.entities import Match, MatchResult, MatchStatus
from app.domain.phases.entities import Phase, Pool
from app.domain.teams.entities import Team
from app.domain.users.entities import User
from app.infrastructure.persistence import mappers as mp
from app.infrastructure.persistence.models import (
    AuditEventModel,
    CompetitionModel,
    MatchModel,
    MatchResultModel,
    PhaseModel,
    PoolModel,
    SeasonModel,
    TeamModel,
    UserModel,
)


class SqlSeasonRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, season: Season) -> Season:
        model = mp.season_to_model(season)
        self._db.add(model)
        self._db.flush()
        return mp.season_to_domain(model)

    def get(self, season_id: uuid.UUID) -> Season | None:
        model = self._db.get(SeasonModel, season_id)
        return mp.season_to_domain(model) if model else None

    def list(self) -> list[Season]:
        models = self._db.scalars(select(SeasonModel)).all()
        return [mp.season_to_domain(m) for m in models]


class SqlCompetitionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, competition: Competition) -> Competition:
        model = mp.competition_to_model(competition)
        self._db.add(model)
        self._db.flush()
        return mp.competition_to_domain(model)

    def get(self, competition_id: uuid.UUID) -> Competition | None:
        model = self._db.get(CompetitionModel, competition_id)
        return mp.competition_to_domain(model) if model else None

    def list(self, limit: int = 50, offset: int = 0) -> tuple[list[Competition], int]:
        total_count = self._db.scalar(select(func.count()).select_from(CompetitionModel)) or 0
        models = self._db.scalars(select(CompetitionModel).limit(limit).offset(offset)).all()
        return [mp.competition_to_domain(m) for m in models], total_count

    def list_published(self, limit: int = 50, offset: int = 0) -> tuple[list[Competition], int]:
        """Used by the public, unauthenticated API surface: filters at
        the SQL level (not in-memory) so that pagination stays correct."""
        base_filter = (CompetitionModel.is_published.is_(True)) & (CompetitionModel.status == "ACTIVE")
        total_count = self._db.scalar(select(func.count()).select_from(CompetitionModel).where(base_filter)) or 0
        models = self._db.scalars(
            select(CompetitionModel).where(base_filter).limit(limit).offset(offset)
        ).all()
        return [mp.competition_to_domain(m) for m in models], total_count

    def update(self, competition: Competition) -> Competition:
        model = self._db.get(CompetitionModel, competition.id)
        if model is None:
            raise ValueError("Competition not found for update.")
        for field in ("name", "category", "gender", "is_published", "updated_at"):
            setattr(model, field, getattr(competition, field))
        model.status = competition.status.value
        model.type = competition.type.value
        self._db.flush()
        return mp.competition_to_domain(model)


class SqlTeamRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, team: Team) -> Team:
        model = mp.team_to_model(team)
        self._db.add(model)
        self._db.flush()
        return mp.team_to_domain(model)

    def get(self, team_id: uuid.UUID) -> Team | None:
        model = self._db.get(TeamModel, team_id)
        return mp.team_to_domain(model) if model else None

    def list_by_competition(self, competition_id: uuid.UUID) -> list[Team]:
        models = self._db.scalars(select(TeamModel).where(TeamModel.competition_id == competition_id)).all()
        return [mp.team_to_domain(m) for m in models]

    def update(self, team: Team) -> Team:
        model = self._db.get(TeamModel, team.id)
        if model is None:
            raise ValueError("Team not found for update.")
        model.name = team.name
        model.club_name = team.club_name
        model.pool_id = team.pool_id
        model.updated_at = team.updated_at
        self._db.flush()
        return mp.team_to_domain(model)


class SqlPhaseRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, phase: Phase) -> Phase:
        model = mp.phase_to_model(phase)
        self._db.add(model)
        self._db.flush()
        return mp.phase_to_domain(model)

    def get(self, phase_id: uuid.UUID) -> Phase | None:
        model = self._db.get(PhaseModel, phase_id)
        return mp.phase_to_domain(model) if model else None

    def list_by_competition(self, competition_id: uuid.UUID) -> list[Phase]:
        models = self._db.scalars(
            select(PhaseModel).where(PhaseModel.competition_id == competition_id).order_by(PhaseModel.order)
        ).all()
        return [mp.phase_to_domain(m) for m in models]


class SqlPoolRepository:
    """Pool.team_ids is derived from the teams table (a team points to
    its pool_id) rather than duplicated in an association table."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _team_ids_for(self, pool_id: uuid.UUID) -> list[uuid.UUID]:
        rows = self._db.scalars(select(TeamModel.id).where(TeamModel.pool_id == pool_id)).all()
        return list(rows)

    def add(self, pool: Pool) -> Pool:
        model = mp.pool_to_model(pool)
        self._db.add(model)
        self._db.flush()
        return mp.pool_to_domain(model, self._team_ids_for(model.id))

    def get(self, pool_id: uuid.UUID) -> Pool | None:
        model = self._db.get(PoolModel, pool_id)
        if model is None:
            return None
        return mp.pool_to_domain(model, self._team_ids_for(pool_id))

    def list_by_phase(self, phase_id: uuid.UUID) -> list[Pool]:
        models = self._db.scalars(select(PoolModel).where(PoolModel.phase_id == phase_id)).all()
        return [mp.pool_to_domain(m, self._team_ids_for(m.id)) for m in models]

    def update(self, pool: Pool) -> Pool:
        # team_ids is derived, nothing to persist on the pool row itself
        # beyond name/updated_at -- membership changes go through TeamRepository.
        model = self._db.get(PoolModel, pool.id)
        if model is None:
            raise ValueError("Pool not found for update.")
        model.name = pool.name
        model.updated_at = pool.updated_at
        self._db.flush()
        return mp.pool_to_domain(model, self._team_ids_for(pool.id))


class SqlMatchRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, match: Match) -> Match:
        model = mp.match_to_model(match)
        self._db.add(model)
        self._db.flush()
        return mp.match_to_domain(model)

    def add_many(self, matches: list[Match]) -> list[Match]:
        models = [mp.match_to_model(m) for m in matches]
        self._db.add_all(models)
        self._db.flush()
        return [mp.match_to_domain(m) for m in models]

    def get(self, match_id: uuid.UUID) -> Match | None:
        model = self._db.get(MatchModel, match_id)
        return mp.match_to_domain(model) if model else None

    def list_by_competition(self, competition_id: uuid.UUID) -> list[Match]:
        # V1: competitions -> phases -> pools -> matches
        pool_ids = self._db.scalars(
            select(PoolModel.id).join(PhaseModel, PoolModel.phase_id == PhaseModel.id).where(
                PhaseModel.competition_id == competition_id
            )
        ).all()
        if not pool_ids:
            return []
        models = self._db.scalars(select(MatchModel).where(MatchModel.pool_id.in_(pool_ids))).all()
        return [mp.match_to_domain(m) for m in models]

    def list_by_pool(self, pool_id: uuid.UUID) -> list[Match]:
        models = self._db.scalars(
            select(MatchModel).where(MatchModel.pool_id == pool_id).order_by(MatchModel.scheduled_at)
        ).all()
        return [mp.match_to_domain(m) for m in models]

    def update(self, match: Match) -> Match:
        model = self._db.get(MatchModel, match.id)
        if model is None:
            raise ValueError("Match not found for update.")
        model.scheduled_at = match.scheduled_at
        model.venue_id = match.venue_id
        model.status = match.status.value
        model.updated_at = match.updated_at
        self._db.flush()
        return mp.match_to_domain(model)

    def delete_unplayed_by_pool(self, pool_id: uuid.UUID) -> None:
        models = self._db.scalars(
            select(MatchModel).where(MatchModel.pool_id == pool_id, MatchModel.status != MatchStatus.PLAYED.value)
        ).all()
        for m in models:
            self._db.delete(m)
        self._db.flush()

    def has_played_matches(self, pool_id: uuid.UUID) -> bool:
        row = self._db.scalars(
            select(MatchModel.id).where(MatchModel.pool_id == pool_id, MatchModel.status == MatchStatus.PLAYED.value)
        ).first()
        return row is not None


class SqlMatchResultRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, result: MatchResult) -> MatchResult:
        model = mp.result_to_model(result)
        self._db.add(model)
        self._db.flush()
        return mp.result_to_domain(model)

    def get_by_match(self, match_id: uuid.UUID) -> MatchResult | None:
        model = self._db.scalars(select(MatchResultModel).where(MatchResultModel.match_id == match_id)).first()
        return mp.result_to_domain(model) if model else None

    def update(self, result: MatchResult) -> MatchResult:
        model = self._db.get(MatchResultModel, result.id)
        if model is None:
            raise ValueError("MatchResult not found for update.")
        model.home_score = result.home_score
        model.away_score = result.away_score
        model.is_validated = result.is_validated
        model.correction_count = result.correction_count
        model.updated_at = result.updated_at
        self._db.flush()
        return mp.result_to_domain(model)

    def list_by_pool(self, pool_id: uuid.UUID) -> list[MatchResult]:
        models = self._db.scalars(
            select(MatchResultModel)
            .join(MatchModel, MatchResultModel.match_id == MatchModel.id)
            .where(MatchModel.pool_id == pool_id)
        ).all()
        return [mp.result_to_domain(m) for m in models]


class SqlUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, user_id: uuid.UUID) -> User | None:
        model = self._db.get(UserModel, user_id)
        return mp.user_to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self._db.scalars(select(UserModel).where(UserModel.email == email)).first()
        return mp.user_to_domain(model) if model else None

    def add(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
        )
        self._db.add(model)
        self._db.flush()
        return mp.user_to_domain(model)


class SqlAuditRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, event: AuditEvent) -> AuditEvent:
        model = mp.audit_to_model(event)
        self._db.add(model)
        self._db.flush()
        return mp.audit_to_domain(model)

    def list_by_entity(self, entity_type: str, entity_id: uuid.UUID) -> list[AuditEvent]:
        models = self._db.scalars(
            select(AuditEventModel)
            .where(AuditEventModel.entity_type == entity_type, AuditEventModel.entity_id == entity_id)
            .order_by(AuditEventModel.occurred_at.desc())
        ).all()
        return [mp.audit_to_domain(m) for m in models]

    def list_all(self, limit: int = 50, offset: int = 0) -> tuple[list[AuditEvent], int]:
        total = self._db.scalar(select(func.count()).select_from(AuditEventModel)) or 0
        models = self._db.scalars(
            select(AuditEventModel).order_by(AuditEventModel.occurred_at.desc()).limit(limit).offset(offset)
        ).all()
        return [mp.audit_to_domain(m) for m in models], total
