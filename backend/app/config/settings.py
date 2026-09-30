from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "COMPET LAB"
    environment: str = "local"

    database_url: str = "postgresql+psycopg://compet:compet@localhost:5432/compet_lab"

    jwt_secret: str = "dev-only-jwt-secret-change-me-before-any-real-deployment"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 8

    cors_origins: list[str] = ["http://localhost:4200"]


settings = Settings()
