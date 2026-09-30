"""Conversion functions between domain entities and SQLAlchemy models.

Kept separate from the repositories themselves purely for readability.
"""
from __future__ import annotations

from app.domain.competitions.entities import Competition, CompetitionStatus, CompetitionType, Season
from app.domain.matches.entities import Match, MatchResult, MatchStatus
from app.domain.phases.entities import Phase, Pool
from app.domain.teams.entities import Team
from app.domain.users.entities import Role, User
from app.domain.audit.entities import AuditEvent
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


def season_to_domain(m: SeasonModel) -> Season:
    return Season(id=m.id, created_at=m.created_at, updated_at=m.updated_at, label=m.label, is_current=m.is_current)


def season_to_model(e: Season) -> SeasonModel:
    return SeasonModel(
        id=e.id, created_at=e.created_at, updated_at=e.updated_at, label=e.label, is_current=e.is_current
    )


def competition_to_domain(m: CompetitionModel) -> Competition:
    return Competition(
        id=m.id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        season_id=m.season_id,
        name=m.name,
        category=m.category,
        gender=m.gender,
        type=CompetitionType(m.type),
        status=CompetitionStatus(m.status),
        is_published=m.is_published,
        legacy_id=m.legacy_id,
    )


def competition_to_model(e: Competition) -> CompetitionModel:
    return CompetitionModel(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        season_id=e.season_id,
        name=e.name,
        category=e.category,
        gender=e.gender,
        type=e.type.value,
        status=e.status.value,
        is_published=e.is_published,
        legacy_id=e.legacy_id,
    )


def team_to_domain(m: TeamModel) -> Team:
    return Team(
        id=m.id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        competition_id=m.competition_id,
        name=m.name,
        club_name=m.club_name,
        pool_id=m.pool_id,
        legacy_id=m.legacy_id,
    )


def team_to_model(e: Team) -> TeamModel:
    return TeamModel(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        competition_id=e.competition_id,
        name=e.name,
        club_name=e.club_name,
        pool_id=e.pool_id,
        legacy_id=e.legacy_id,
    )


def phase_to_domain(m: PhaseModel) -> Phase:
    return Phase(
        id=m.id, created_at=m.created_at, updated_at=m.updated_at,
        competition_id=m.competition_id, name=m.name, order=m.order,
    )


def phase_to_model(e: Phase) -> PhaseModel:
    return PhaseModel(
        id=e.id, created_at=e.created_at, updated_at=e.updated_at,
        competition_id=e.competition_id, name=e.name, order=e.order,
    )


def pool_to_domain(m: PoolModel, team_ids: list) -> Pool:
    return Pool(
        id=m.id, created_at=m.created_at, updated_at=m.updated_at,
        phase_id=m.phase_id, name=m.name, team_ids=list(team_ids),
    )


def pool_to_model(e: Pool) -> PoolModel:
    return PoolModel(id=e.id, created_at=e.created_at, updated_at=e.updated_at, phase_id=e.phase_id, name=e.name)


def match_to_domain(m: MatchModel) -> Match:
    return Match(
        id=m.id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        pool_id=m.pool_id,
        home_team_id=m.home_team_id,
        away_team_id=m.away_team_id,
        scheduled_at=m.scheduled_at,
        venue_id=m.venue_id,
        status=MatchStatus(m.status),
        legacy_id=m.legacy_id,
    )


def match_to_model(e: Match) -> MatchModel:
    return MatchModel(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        pool_id=e.pool_id,
        home_team_id=e.home_team_id,
        away_team_id=e.away_team_id,
        scheduled_at=e.scheduled_at,
        venue_id=e.venue_id,
        status=e.status.value,
        legacy_id=e.legacy_id,
    )


def result_to_domain(m: MatchResultModel) -> MatchResult:
    return MatchResult(
        id=m.id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        match_id=m.match_id,
        home_score=m.home_score,
        away_score=m.away_score,
        is_validated=m.is_validated,
        correction_count=m.correction_count,
    )


def result_to_model(e: MatchResult) -> MatchResultModel:
    return MatchResultModel(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        match_id=e.match_id,
        home_score=e.home_score,
        away_score=e.away_score,
        is_validated=e.is_validated,
        correction_count=e.correction_count,
    )


def user_to_domain(m: UserModel) -> User:
    return User(
        id=m.id, created_at=m.created_at, updated_at=m.updated_at,
        email=m.email, hashed_password=m.hashed_password, full_name=m.full_name,
        role=Role(m.role), is_active=m.is_active,
    )


def audit_to_domain(m: AuditEventModel) -> AuditEvent:
    return AuditEvent(
        id=m.id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        actor_id=m.actor_id,
        actor_email=m.actor_email,
        action=m.action,
        entity_type=m.entity_type,
        entity_id=m.entity_id,
        old_value=m.old_value,
        new_value=m.new_value,
        occurred_at=m.occurred_at,
    )


def audit_to_model(e: AuditEvent) -> AuditEventModel:
    return AuditEventModel(
        id=e.id,
        created_at=e.created_at,
        updated_at=e.updated_at,
        actor_id=e.actor_id,
        actor_email=e.actor_email,
        action=e.action,
        entity_type=e.entity_type,
        entity_id=e.entity_id,
        old_value=e.old_value,
        new_value=e.new_value,
        occurred_at=e.occurred_at,
    )
