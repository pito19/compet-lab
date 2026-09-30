"""add indexes on foreign key columns

PostgreSQL does not automatically index foreign key columns (unlike
primary keys). Every repository method filtering by pool_id,
competition_id, phase_id, etc. (i.e. most of the application's read
paths) would otherwise degrade to a sequential scan as tables grow.

Revision ID: 0002_fk_indexes
Revises: 0001_initial
Create Date: 2026-09-29

"""
from alembic import op

revision = "0002_fk_indexes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

_INDEXES = [
    ("ix_competitions_season_id", "competitions", ["season_id"]),
    ("ix_teams_competition_id", "teams", ["competition_id"]),
    ("ix_teams_pool_id", "teams", ["pool_id"]),
    ("ix_phases_competition_id", "phases", ["competition_id"]),
    ("ix_pools_phase_id", "pools", ["phase_id"]),
    ("ix_matches_pool_id", "matches", ["pool_id"]),
    ("ix_matches_home_team_id", "matches", ["home_team_id"]),
    ("ix_matches_away_team_id", "matches", ["away_team_id"]),
    # Composite: list_by_entity() filters on both columns together.
    ("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id"]),
    # list_all() always orders by occurred_at desc.
    ("ix_audit_events_occurred_at", "audit_events", ["occurred_at"]),
]


def upgrade() -> None:
    for name, table, columns in _INDEXES:
        op.create_index(name, table, columns)


def downgrade() -> None:
    for name, table, _columns in reversed(_INDEXES):
        op.drop_index(name, table_name=table)
