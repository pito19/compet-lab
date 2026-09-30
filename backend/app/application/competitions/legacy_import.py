from __future__ import annotations

import uuid

from app.domain.shared.ports import CompetitionRepository
from app.infrastructure.legacy.adapter import LegacyCompetitionAdapter
from app.infrastructure.legacy.models import LegacyCompetitionRecord


class LegacyCompetitionImportService:
    """Progressive migration use case: takes legacy records, converts
    them through the Anti-Corruption Layer, and persists them as
    first-class modern Competitions -- keeping the legacy_id around
    purely as a traceability/mapping field, never as a foreign key
    relied upon by business rules.
    """

    def __init__(self, repo: CompetitionRepository) -> None:
        self._repo = repo

    def import_record(self, record: LegacyCompetitionRecord, season_id: uuid.UUID):
        competition = LegacyCompetitionAdapter.to_domain(record, season_id)
        return self._repo.add(competition)

    def import_batch(self, records: list[LegacyCompetitionRecord], season_id: uuid.UUID) -> list:
        return [self.import_record(r, season_id) for r in records]
