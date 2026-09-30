from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.competitions.schemas import CompetitionResponse
from app.application.competitions.legacy_import import LegacyCompetitionImportService
from app.application.shared.context import ActorContext
from app.infrastructure.legacy.models import LegacyCompetitionRecord
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import SqlCompetitionRepository
from app.infrastructure.security.auth import require_admin

router = APIRouter(prefix="/api/legacy", tags=["legacy"])


class LegacyCompetitionImportRequest(BaseModel):
    """Mirrors the shape of a record as it would come out of the
    simulated legacy source (see infrastructure/legacy/models.py):
    free-text status, legacy vocabulary, no validated enums. The
    Anti-Corruption Layer (LegacyCompetitionAdapter) is what converts
    this into a first-class modern Competition.
    """

    legacy_id: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=200)
    category_code: str = Field(min_length=1, max_length=50, examples=["U15"])
    kind: str = Field(examples=["CHAMPIONNAT", "COUPE", "TOURNOI"])
    active_flag: str = Field(examples=["O", "N"], min_length=1, max_length=1)
    season_id: uuid.UUID


@router.post("/import-competition", response_model=CompetitionResponse)
def import_legacy_competition(
    payload: LegacyCompetitionImportRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(require_admin),
):
    service = LegacyCompetitionImportService(SqlCompetitionRepository(db))
    record = LegacyCompetitionRecord(
        legacy_id=payload.legacy_id,
        label=payload.label,
        category_code=payload.category_code,
        kind=payload.kind,
        active_flag=payload.active_flag,
    )
    competition = service.import_record(record, payload.season_id)
    return CompetitionResponse.from_domain(competition)
