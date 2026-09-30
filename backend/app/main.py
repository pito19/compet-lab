from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.audit.router import router as audit_router
from app.api.auth.router import router as auth_router
from app.api.competitions.router import router as competitions_router
from app.api.error_handlers import register_error_handlers
from app.api.legacy.router import router as legacy_router
from app.api.matches.router import router as matches_router
from app.api.phases.router import router as phases_router
from app.api.public.router import router as public_router
from app.api.rankings.router import router as rankings_router
from app.api.results.router import router as results_router
from app.api.seasons.router import router as seasons_router
from app.api.teams.router import router as teams_router
from app.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "COMPET LAB -- Modern Competition Management & Operations. "
        "Prototype architecture inspired by the public functional domain of "
        "sports competition management; not a reproduction of any specific "
        "internal system."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth_router)
app.include_router(seasons_router)
app.include_router(competitions_router)
app.include_router(teams_router)
app.include_router(phases_router)
app.include_router(matches_router)
app.include_router(results_router)
app.include_router(rankings_router)
app.include_router(audit_router)
app.include_router(legacy_router)
app.include_router(public_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.app_name}
