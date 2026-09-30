from __future__ import annotations

import uuid
from datetime import datetime, timedelta


def generate_round_robin_pairings(team_ids: list[uuid.UUID]) -> list[list[tuple[uuid.UUID, uuid.UUID]]]:
    """Single round-robin (each team plays every other team exactly
    once). Returns a list of matchdays, each matchday being a list of
    (home, away) pairs.

    Standard circle method. If the number of teams is odd, a "bye"
    (None) rotates through and is simply dropped from each matchday.
    """
    teams: list[uuid.UUID | None] = list(team_ids)
    if len(teams) < 2:
        return []

    if len(teams) % 2 == 1:
        teams.append(None)  # bye

    n = len(teams)
    matchdays: list[list[tuple[uuid.UUID, uuid.UUID]]] = []

    fixed = teams[0]
    rotating = teams[1:]

    for _round in range(n - 1):
        current = [fixed] + rotating
        pairs: list[tuple[uuid.UUID, uuid.UUID]] = []
        for i in range(n // 2):
            home, away = current[i], current[n - 1 - i]
            if home is not None and away is not None:
                pairs.append((home, away))
        matchdays.append(pairs)
        rotating = [rotating[-1]] + rotating[:-1]

    return matchdays


def default_kickoff_times(
    start_date: datetime,
    matchday_count: int,
    days_between_matchdays: int = 7,
) -> list[datetime]:
    """V1 keeps scheduling simple and deterministic: one matchday per
    week, all kicking off at the same start_date time-of-day."""
    return [start_date + timedelta(days=days_between_matchdays * i) for i in range(matchday_count)]
