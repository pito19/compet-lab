import uuid
from datetime import datetime, timezone

from app.application.scheduling.round_robin import default_kickoff_times, generate_round_robin_pairings


def test_round_robin_even_number_of_teams():
    teams = [uuid.uuid4() for _ in range(8)]
    matchdays = generate_round_robin_pairings(teams)

    assert len(matchdays) == 7
    for matchday in matchdays:
        assert len(matchday) == 4

    all_pairs = set()
    for matchday in matchdays:
        for home, away in matchday:
            pair = frozenset((home, away))
            assert pair not in all_pairs
            all_pairs.add(pair)
    assert len(all_pairs) == 28  # 8 * 7 / 2


def test_round_robin_odd_number_of_teams_has_one_bye_per_matchday():
    teams = [uuid.uuid4() for _ in range(7)]
    matchdays = generate_round_robin_pairings(teams)

    assert len(matchdays) == 7
    for matchday in matchdays:
        assert len(matchday) == 3  # one team rests every matchday


def test_round_robin_less_than_two_teams_returns_empty():
    assert generate_round_robin_pairings([]) == []
    assert generate_round_robin_pairings([uuid.uuid4()]) == []


def test_default_kickoff_times_are_spaced_correctly():
    start = datetime(2027, 3, 1, 14, 0, tzinfo=timezone.utc)
    kickoffs = default_kickoff_times(start, matchday_count=5, days_between_matchdays=7)

    assert len(kickoffs) == 5
    assert kickoffs[0] == start
    for i in range(1, len(kickoffs)):
        assert (kickoffs[i] - kickoffs[i - 1]).days == 7
