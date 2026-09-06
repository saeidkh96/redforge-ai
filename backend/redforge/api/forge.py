from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from redforge.agents import OpenAICompatibleProvider
from redforge.core.config import get_settings
from redforge.core.orchestrator import ForgeOrchestrator
from redforge.models import ForgeRun, Issue

router = APIRouter(prefix="/api/v1/forge", tags=["forge"])


class ForgeRunRequest(BaseModel):
    repository_path: str
    issue: Issue
    generate_patch: bool = False
    apply_patch: bool = False
    repair_on_failure: bool | None = None
    max_repair_attempts: int | None = Field(default=None, ge=0, le=10)


def _provider() -> OpenAICompatibleProvider | None:
    settings = get_settings()
    if not settings.llm_base_url or not settings.llm_model:
        return None
    return OpenAICompatibleProvider(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
    )


@router.post("/runs", response_model=ForgeRun)
def create_forge_run(request: ForgeRunRequest) -> ForgeRun:
    if request.apply_patch and not request.generate_patch:
        raise HTTPException(
            status_code=400,
            detail="apply_patch requires generate_patch=true",
        )

    settings = get_settings()
    repair_on_failure = (
        settings.repair_on_failure
        if request.repair_on_failure is None
        else request.repair_on_failure
    )
    max_repair_attempts = (
        settings.max_repair_attempts
        if request.max_repair_attempts is None
        else request.max_repair_attempts
    )

    return ForgeOrchestrator(provider=_provider()).run(
        Path(request.repository_path),
        request.issue,
        generate_patch=request.generate_patch,
        apply_patch=request.apply_patch,
        repair_on_failure=repair_on_failure,
        max_repair_attempts=max_repair_attempts,
    )
