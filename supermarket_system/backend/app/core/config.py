from __future__ import annotations

import uuid
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Supermarket Product Management System"
    environment: str = "development"
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173"]

    @staticmethod
    def new_request_id() -> str:
        return str(uuid.uuid4())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
