from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from redforge.roadmap_v140 import GitHubAutonomyPlanner, GitHubIssueEvent, PythonImpactAnalyzer

router = APIRouter(prefix="/api/v1/autonomy", tags=["autonomy"])


class ImpactRequest(BaseModel):
    repository_path: str
    changed_files: list[str] = Field(default_factory=list)


class IssueEnvelopeRequest(BaseModel):
    owner: str
    repo: str
    issue_number: int = Field(ge=1)
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    sender: str | None = None


@router.post("/impact")
def analyze_impact(request: ImpactRequest) -> dict[str, Any]:
    return (
        PythonImpactAnalyzer()
        .analyze(Path(request.repository_path), request.changed_files)
        .model_dump(mode="json")
    )


@router.post("/github-issue/envelope")
def github_issue_envelope(request: IssueEnvelopeRequest) -> dict[str, Any]:
    event = GitHubIssueEvent(**request.model_dump())
    planner = GitHubAutonomyPlanner()
    return {
        "branch": planner.branch_for(event),
        "repository_url": planner.repository_url(event),
        "prompt": planner.issue_prompt(event),
        "workspace_name": planner.workspace_name(event),
    }
