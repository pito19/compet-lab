from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.shared.base import Entity, utc_now


@dataclass
class AuditEvent(Entity):
    """Append-only. Never updated, never deleted."""

    actor_id: uuid.UUID | None = None
    actor_email: str = ""
    action: str = ""  # e.g. "MATCH_RESCHEDULED", "RESULT_CORRECTED"
    entity_type: str = ""
    entity_id: uuid.UUID | None = None
    old_value: dict = field(default_factory=dict)
    new_value: dict = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=utc_now)
