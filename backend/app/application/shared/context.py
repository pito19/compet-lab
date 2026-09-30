from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.users.entities import Role


@dataclass(frozen=True)
class ActorContext:
    """Represents 'who is performing the operation' from the point of
    view of the application layer.

    This type is owned by the application layer, not by the security
    infrastructure. The API layer is responsible for translating a
    validated JWT/session into an ActorContext before invoking any
    application service. This keeps application services testable
    without any real authentication mechanism.
    """

    id: uuid.UUID
    email: str
    role: Role

    def can_write(self) -> bool:
        return self.role in (Role.ADMIN, Role.MANAGER)

    def can_administrate(self) -> bool:
        return self.role == Role.ADMIN
