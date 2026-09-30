from __future__ import annotations

from http.client import responses as HTTP_REASON_PHRASES

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.shared.exceptions import ConflictError, DomainError, InvalidStateError, NotFoundError, ValidationError

_STATUS_MAP = {
    NotFoundError: 404,
    ConflictError: 409,
    InvalidStateError: 409,
    ValidationError: 422,
}

_PROBLEM_TYPE_BASE = "/problems"


def _problem_type(exc: DomainError) -> str:
    # e.g. NOT_FOUND -> /problems/not-found
    return f"{_PROBLEM_TYPE_BASE}/{exc.code.lower().replace('_', '-')}"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code = _STATUS_MAP.get(type(exc), 400)
        return JSONResponse(
            status_code=status_code,
            media_type="application/problem+json",
            content={
                "type": _problem_type(exc),
                "title": exc.code.replace("_", " ").title(),
                "status": status_code,
                "detail": exc.message,
                "instance": str(request.url.path),
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            media_type="application/problem+json",
            content={
                "type": f"{_PROBLEM_TYPE_BASE}/request-validation-error",
                "title": "Request Validation Error",
                "status": 422,
                "detail": "One or more fields failed validation.",
                "instance": str(request.url.path),
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Catches every plain `raise HTTPException(...)` in the codebase
        (401/403 from the auth dependencies, 404s in the public router,
        FastAPI's own 404 for unknown routes, etc.) so that EVERY error
        response from this API -- not just domain errors -- uses the same
        application/problem+json shape. Without this, a client had to
        handle two different error formats depending on which layer
        raised the error, which is exactly the kind of inconsistency a
        senior API review would flag.
        """
        title = HTTP_REASON_PHRASES.get(exc.status_code, "Error")
        detail = exc.detail if isinstance(exc.detail, str) else title
        return JSONResponse(
            status_code=exc.status_code,
            media_type="application/problem+json",
            headers=exc.headers,
            content={
                "type": f"{_PROBLEM_TYPE_BASE}/{title.lower().replace(' ', '-')}",
                "title": title,
                "status": exc.status_code,
                "detail": detail,
                "instance": str(request.url.path),
            },
        )
