import uuid
from datetime import datetime, timezone

import pytest

from app.domain.competitions.entities import Competition
from app.domain.matches.entities import Match
from app.domain.phases.entities import Pool
from app.domain.shared.exceptions import ConflictError, InvalidStateError, ValidationError


def test_pool_rejects_duplicate_team():
    pool = Pool(phase_id=uuid.uuid4(), name="Poule A")
    team_id = uuid.uuid4()
    pool.add_team(team_id)

    with pytest.raises(ConflictError):
        pool.add_team(team_id)


def test_pool_remove_team_is_idempotent():
    pool = Pool(phase_id=uuid.uuid4(), name="Poule A")
    team_id = uuid.uuid4()
    pool.add_team(team_id)
    pool.remove_team(team_id)
    pool.remove_team(team_id)  # should not raise
    assert team_id not in pool.team_ids


def test_match_cannot_oppose_a_team_to_itself():
    team_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        Match(home_team_id=team_id, away_team_id=team_id)


def test_played_match_cannot_be_rescheduled():
    match = Match(home_team_id=uuid.uuid4(), away_team_id=uuid.uuid4())
    match.mark_played()

    with pytest.raises(InvalidStateError):
        match.reschedule(datetime.now(timezone.utc))


def test_played_match_cannot_be_postponed_or_cancelled():
    match = Match(home_team_id=uuid.uuid4(), away_team_id=uuid.uuid4())
    match.mark_played()

    with pytest.raises(InvalidStateError):
        match.postpone()
    with pytest.raises(InvalidStateError):
        match.cancel()


def test_cancelled_match_status_is_reachable_for_result_service_guard():
    """ResultService.record_result() rejects results on a CANCELLED
    match (see application/results/use_cases.py) -- this test locks in
    the domain-level precondition that guard relies on."""
    match = Match(home_team_id=uuid.uuid4(), away_team_id=uuid.uuid4())
    match.cancel()
    assert match.status.value == "CANCELLED"


def test_closed_competition_cannot_be_reactivated():
    competition = Competition(name="Test Cup")
    competition.activate()
    competition.close()

    with pytest.raises(InvalidStateError):
        competition.activate()


def test_only_active_competition_can_be_published():
    competition = Competition(name="Test Cup")
    with pytest.raises(InvalidStateError):
        competition.publish()

    competition.activate()
    competition.publish()
    assert competition.is_published is True


def test_closing_a_competition_unpublishes_it():
    competition = Competition(name="Test Cup")
    competition.activate()
    competition.publish()
    competition.close()
    assert competition.is_published is False
