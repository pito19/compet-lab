"""Shared building blocks for domain entities.

Pure Python. No ORM, no Pydantic, no FastAPI import allowed in this
package -- that is the whole point of the domain layer.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def new_id() -> uuid.UUID:
    return uuid.uuid4()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Entity:
    """Base class for entities with identity."""

    id: uuid.UUID = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()
