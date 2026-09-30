"""Seed script: creates the 3 demo accounts (ADMIN/MANAGER/VIEWER) and a
minimal demo dataset (one season, one competition, one phase/pool with
8 teams) so the application is immediately explorable after a fresh
`docker compose up`.

Run with: python -m app.seed
"""
from __future__ import annotations

from app.domain.competitions.entities import Competition, CompetitionStatus, CompetitionType, Season
from app.domain.phases.entities import Phase, Pool
from app.domain.teams.entities import Team
from app.domain.users.entities import Role, User
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.repositories import (
    SqlCompetitionRepository,
    SqlPhaseRepository,
    SqlPoolRepository,
    SqlSeasonRepository,
    SqlTeamRepository,
    SqlUserRepository,
)
from app.infrastructure.security.passwords import hash_password

DEMO_ACCOUNTS = [
    ("admin@compet-lab.local", "Admin123!", Role.ADMIN, "Alice Admin"),
    ("manager@compet-lab.local", "Manager123!", Role.MANAGER, "Marc Manager"),
    ("viewer@compet-lab.local", "Viewer123!", Role.VIEWER, "Vera Viewer"),
]

DEMO_TEAMS = [
    # Real, publicly known French club names used purely for demo realism.
    # This dataset is fictional: no real club is actually registered in
    # this prototype competition, and no real player data is involved.
    ("Paris Saint-Germain U15", "Paris Saint-Germain"),
    ("Olympique de Marseille U15", "Olympique de Marseille"),
    ("AS Monaco U15", "AS Monaco"),
    ("Olympique Lyonnais U15", "Olympique Lyonnais"),
    ("LOSC Lille U15", "LOSC Lille"),
    ("Stade Rennais U15", "Stade Rennais FC"),
    ("RC Lens U15", "Racing Club de Lens"),
    ("OGC Nice U15", "OGC Nice"),
]


def run() -> None:
    db = SessionLocal()
    try:
        users = SqlUserRepository(db)
        for email, password, role, full_name in DEMO_ACCOUNTS:
            if users.get_by_email(email) is None:
                users.add(User(email=email, hashed_password=hash_password(password), role=role, full_name=full_name))
                print(f"[seed] created user {email} ({role.value})")
            else:
                print(f"[seed] user {email} already exists, skipping")

        seasons = SqlSeasonRepository(db)
        competitions = SqlCompetitionRepository(db)

        demo_competition_name = "U15 Régional 1 - Poule Unique"
        existing = next((c for c in competitions.list(limit=200)[0] if c.name == demo_competition_name), None)

        if existing is not None:
            print(f"[seed] demo dataset already present ('{demo_competition_name}'), skipping")
        else:
            season = seasons.add(Season(label="2026/2027", is_current=True))
            print(f"[seed] created season {season.label}")

            competition = competitions.add(
                Competition(
                    season_id=season.id,
                    name=demo_competition_name,
                    category="U15",
                    gender="MIXED",
                    type=CompetitionType.CHAMPIONSHIP,
                    status=CompetitionStatus.ACTIVE,
                    is_published=True,
                )
            )
            print(f"[seed] created competition {competition.name}")

            phases = SqlPhaseRepository(db)
            phase = phases.add(Phase(competition_id=competition.id, name="Phase Régulière", order=1))

            pools = SqlPoolRepository(db)
            pool = pools.add(Pool(phase_id=phase.id, name="Poule A"))

            teams_repo = SqlTeamRepository(db)
            for name, club_name in DEMO_TEAMS:
                team = teams_repo.add(Team(competition_id=competition.id, name=name, club_name=club_name))
                team.assign_to_pool(pool.id)
                teams_repo.update(team)

            print(f"[seed] created pool '{pool.name}' with {len(DEMO_TEAMS)} teams")

        print("[seed] done. Demo accounts (email / password):")
        for email, password, role, _ in DEMO_ACCOUNTS:
            print(f"    {email} / {password} ({role.value})")

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
