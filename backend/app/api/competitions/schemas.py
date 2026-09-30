from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.competitions.entities import Competition, CompetitionStatus, CompetitionType


class CompetitionCreateRequest(BaseModel):
    season_id: uuid.UUID
    name: str = Field(min_length=2, max_length=200)
    category: str = Field(default="", max_length=50)
    gender: str = Field(default="MIXED", max_length=20)
    type: CompetitionType = CompetitionType.CHAMPIONSHIP


class CompetitionRenameRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)


class CompetitionResponse(BaseModel):
    id: uuid.UUID
    season_id: uuid.UUID | None
    name: str
    category: str
    gender: str
    type: CompetitionType
    status: CompetitionStatus
    is_published: bool
    legacy_id: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, c: Competition) -> "CompetitionResponse":
        return cls(
            id=c.id,
            season_id=c.season_id,
            name=c.name,
            category=c.category,
            gender=c.gender,
            type=c.type,
            status=c.status,
            is_published=c.is_published,
            legacy_id=c.legacy_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )


class CompetitionListResponse(BaseModel):
    items: list[CompetitionResponse]
    total: int
    page: int
    page_size: int
