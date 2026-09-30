from __future__ import annotations

import unicodedata
import uuid
from dataclasses import dataclass


@dataclass
class Standing:
    """A Standing is a computed projection, never edited directly by a
    user. It is recomputed from validated match results every time it
    is requested (or cached and invalidated -- an implementation detail
    of the infrastructure layer, not a domain concern).
    """

    team_id: uuid.UUID
    team_name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws * 1


def _name_sort_key(name: str) -> str:
    """Accent- and case-insensitive sort key for team names.

    Plain code-point comparison would sort "Étoile du Nord" after
    "Union Bellevue" (U+00C9 'É' > 'U'), which reads as wrong to a
    French-speaking user. NFKD-decomposing and dropping combining marks
    gives a locale-independent, dependency-free approximation of
    alphabetical order that does not depend on the OS locale being
    configured (unlike locale.strxfrm, which is fragile in containers).
    """
    decomposed = unicodedata.normalize("NFKD", name)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_accents.casefold()


def sort_key(standing: Standing) -> tuple:
    """V1 fixed ranking policy: points desc, goal difference desc,
    goals for desc, team name asc (deterministic tie-break)."""
    return (
        -standing.points,
        -standing.goal_difference,
        -standing.goals_for,
        _name_sort_key(standing.team_name),
    )
