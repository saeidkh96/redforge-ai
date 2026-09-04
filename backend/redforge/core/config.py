from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RedForge AI"
    version: str = "0.0.1"

    environment: Literal["development", "test", "production"] = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="REDFORGE_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()