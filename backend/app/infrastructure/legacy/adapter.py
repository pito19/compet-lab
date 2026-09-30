"""Anti-Corruption Layer: translates the legacy record shape into the
modern domain, so that the domain never has to know the legacy
vocabulary, encodings or identifier scheme.

This is the piece that lets us claim, truthfully, that the modern
domain does not depend on the legacy model: this adapter is the only
place in the codebase where LegacyCompetitionRecord is imported.
"""
from __future__ import annotations

from app.domain.competitions.entities import Competition, CompetitionStatus, CompetitionType
from app.domain.shared.exceptions import ValidationError
from app.infrastructure.legacy.models import LegacyCompetitionRecord

_KIND_MAPPING = {
    "CHAMPIONNAT": CompetitionType.CHAMPIONSHIP,
    "COUPE": CompetitionType.CUP,
    "TOURNOI": CompetitionType.TOURNAMENT,
}


class LegacyCompetitionAdapter:
    """Converts LegacyCompetitionRecord -> Competition (modern domain).

    Import/migration use cases depend on this adapter, never directly
    on the legacy record shape.
    """

    @staticmethod
    def to_domain(record: LegacyCompetitionRecord, season_id) -> Competition:
        try:
            competition_type = _KIND_MAPPING[record.kind.strip().upper()]
        except KeyError as exc:
            raise ValidationError(
                f"Unknown legacy competition kind: {record.kind!r}",
                {"legacy_id": record.legacy_id},
            ) from exc

        is_active = record.active_flag.strip().upper() == "O"

        return Competition(
            season_id=season_id,
            name=record.label.strip(),
            category=record.category_code.strip().upper(),
            type=competition_type,
            status=CompetitionStatus.ACTIVE if is_active else CompetitionStatus.DRAFT,
            legacy_id=record.legacy_id,
        )
