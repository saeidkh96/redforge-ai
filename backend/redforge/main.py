from fastapi import FastAPI

from redforge.api.forge import router as forge_router
from redforge.api.health import router as health_router
from redforge.api.repository import router as repository_router
from redforge.core.config import get_settings
from redforge.core.logging import configure_logging

configure_logging()
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Agentic software engineering platform.",
)
app.include_router(health_router)
app.include_router(repository_router)
app.include_router(forge_router)
