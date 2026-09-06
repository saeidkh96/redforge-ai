from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from redforge.core.config import get_settings

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    service: str
    status: Literal["healthy"]
    version: str


class ReadinessResponse(BaseModel):
    service: str
    status: Literal["ready"]
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(service="redforge-ai", status="healthy", version=settings.version)


@router.get("/ready", response_model=ReadinessResponse)
def ready() -> ReadinessResponse:
    settings = get_settings()
    return ReadinessResponse(service="redforge-ai", status="ready", version=settings.version)
