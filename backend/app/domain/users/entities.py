from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.domain.shared.base import Entity


class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    VIEWER = "VIEWER"


@dataclass
class User(Entity):
    email: str = ""
    hashed_password: str = ""
    full_name: str = ""
    role: Role = Role.VIEWER
    is_active: bool = True

    def can_write(self) -> bool:
        return self.role in (Role.ADMIN, Role.MANAGER)

    def can_administrate(self) -> bool:
        return self.role == Role.ADMIN
