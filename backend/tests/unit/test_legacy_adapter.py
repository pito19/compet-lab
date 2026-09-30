import uuid

import pytest

from app.domain.competitions.entities import CompetitionStatus, CompetitionType
from app.domain.shared.exceptions import ValidationError
from app.infrastructure.legacy.adapter import LegacyCompetitionAdapter
from app.infrastructure.legacy.models import LegacyCompetitionRecord


def _record(**overrides) -> LegacyCompetitionRecord:
    base = dict(legacy_id="C-1042", label="  U15 Régional 1 ", category_code="u15", kind="championnat", active_flag="O")
    base.update(overrides)
    return LegacyCompetitionRecord(**base)


def test_legacy_record_is_translated_to_modern_domain():
    season_id = uuid.uuid4()

    competition = LegacyCompetitionAdapter.to_domain(_record(), season_id)

    assert competition.name == "U15 Régional 1"  # trimmed
    assert competition.category == "U15"  # normalised
    assert competition.type == CompetitionType.CHAMPIONSHIP  # legacy vocabulary mapped
    assert competition.status == CompetitionStatus.ACTIVE  # "O" flag -> ACTIVE
    assert competition.legacy_id == "C-1042"  # traceability kept
    assert competition.season_id == season_id


def test_inactive_legacy_flag_maps_to_draft():
    competition = LegacyCompetitionAdapter.to_domain(_record(active_flag="N"), uuid.uuid4())
    assert competition.status == CompetitionStatus.DRAFT


@pytest.mark.parametrize("kind,expected", [("COUPE", CompetitionType.CUP), ("TOURNOI", CompetitionType.TOURNAMENT)])
def test_other_legacy_kinds_are_mapped(kind, expected):
    assert LegacyCompetitionAdapter.to_domain(_record(kind=kind), uuid.uuid4()).type == expected


def test_unknown_legacy_kind_is_rejected_with_a_domain_error():
    with pytest.raises(ValidationError):
        LegacyCompetitionAdapter.to_domain(_record(kind="MYSTERE"), uuid.uuid4())
