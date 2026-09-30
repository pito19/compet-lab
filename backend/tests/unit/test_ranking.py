import uuid

from app.domain.rankings.entities import Standing, sort_key


def _standing(name, wins=0, draws=0, losses=0, gf=0, ga=0) -> Standing:
    return Standing(
        team_id=uuid.uuid4(), team_name=name, played=wins + draws + losses,
        wins=wins, draws=draws, losses=losses, goals_for=gf, goals_against=ga,
    )


def test_points_are_computed_correctly():
    s = _standing("Alpha", wins=3, draws=2, losses=1)
    assert s.points == 3 * 3 + 2 * 1


def test_goal_difference_is_computed_correctly():
    s = _standing("Alpha", gf=10, ga=4)
    assert s.goal_difference == 6


def test_ranking_sorts_by_points_first():
    leader = _standing("Alpha", wins=5)  # 15 pts
    second = _standing("Bravo", wins=3, draws=1)  # 10 pts

    ranked = sorted([second, leader], key=sort_key)
    assert ranked[0].team_name == "Alpha"


def test_ranking_tie_break_by_goal_difference():
    same_points_better_gd = _standing("Alpha", wins=3, draws=1, gf=10, ga=3)  # 10 pts, GD +7
    same_points_worse_gd = _standing("Bravo", wins=3, draws=1, gf=9, ga=4)  # 10 pts, GD +5

    ranked = sorted([same_points_worse_gd, same_points_better_gd], key=sort_key)
    assert ranked[0].team_name == "Alpha"


def test_ranking_tie_break_by_goals_scored_then_name():
    same_gd_more_goals = _standing("Alpha", wins=3, draws=1, gf=10, ga=5)  # 10 pts, GD +5
    same_gd_fewer_goals = _standing("Bravo", wins=3, draws=1, gf=6, ga=1)  # 10 pts, GD +5

    ranked = sorted([same_gd_fewer_goals, same_gd_more_goals], key=sort_key)
    assert ranked[0].team_name == "Alpha"

    perfectly_tied_a = _standing("Zulu", wins=3, draws=1, gf=6, ga=1)
    perfectly_tied_b = _standing("Alpha", wins=3, draws=1, gf=6, ga=1)
    ranked_alpha_first = sorted([perfectly_tied_a, perfectly_tied_b], key=sort_key)
    assert ranked_alpha_first[0].team_name == "Alpha"  # deterministic alphabetical tie-break


def test_ranking_tie_break_is_accent_insensitive():
    """Regression test: naive code-point comparison sorts 'Étoile...'
    after 'Union...' because U+00C9 ('É') > 'U' as a raw code point,
    which reads as wrong to a French-speaking user. The tie-break must
    ignore accents (and case) to produce the expected alphabetical order."""
    etoile = _standing("Étoile du Nord", wins=3, draws=1, gf=6, ga=1)  # same points/GD/GF as below
    union = _standing("Union Bellevue", wins=3, draws=1, gf=6, ga=1)

    ranked = sorted([union, etoile], key=sort_key)

    assert [s.team_name for s in ranked] == ["Étoile du Nord", "Union Bellevue"]
