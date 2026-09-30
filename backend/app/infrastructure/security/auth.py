from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.shared.context import ActorContext
from app.domain.users.entities import Role
from app.infrastructure.security.jwt import InvalidTokenError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_actor(token: str = Depends(oauth2_scheme)) -> ActorContext:
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.") from exc

    try:
        return ActorContext(id=uuid.UUID(payload["sub"]), email=payload["email"], role=Role(payload["role"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token payload.") from exc


def require_roles(*allowed: Role):
    def dependency(actor: ActorContext = Depends(get_current_actor)) -> ActorContext:
        if actor.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {actor.role.value} is not allowed to perform this operation.",
            )
        return actor

    return dependency


# Convenience shortcuts used across routers.
require_manager_or_admin = require_roles(Role.ADMIN, Role.MANAGER)
require_admin = require_roles(Role.ADMIN)
require_any_role = require_roles(Role.ADMIN, Role.MANAGER, Role.VIEWER)
