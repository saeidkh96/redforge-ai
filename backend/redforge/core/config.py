from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RedForge AI"
    version: str = "1.1.0"
    environment: Literal["development", "test", "production"] = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    workspace_root: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    repair_on_failure: bool = True
    max_repair_attempts: int = 2

    model_config = SettingsConfigDict(
        env_prefix="REDFORGE_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
