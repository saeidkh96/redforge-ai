from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, SecretStr

from redforge.roadmap_v140 import GitHubAutonomyPlanner, GitHubIssueEvent, PythonImpactAnalyzer
from redforge.roadmap_v200 import DeepRepositoryAnalyzer, GitHubIssueClient, GitHubIssueSpec

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


class GitHubIssueFetchRequest(BaseModel):
    owner: str
    repo: str
    issue_number: int = Field(ge=1)
    token: SecretStr


@router.post("/impact")
def analyze_impact(request: ImpactRequest) -> dict[str, Any]:
    return (
        PythonImpactAnalyzer()
        .analyze(Path(request.repository_path), request.changed_files)
        .model_dump(mode="json")
    )


@router.post("/impact/deep")
def analyze_deep_impact(request: ImpactRequest) -> dict[str, Any]:
    return (
        DeepRepositoryAnalyzer()
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


@router.post("/github-issue/fetch", response_model=GitHubIssueSpec)
def fetch_github_issue(request: GitHubIssueFetchRequest) -> GitHubIssueSpec:
    try:
        return GitHubIssueClient(request.token.get_secret_value()).fetch_issue(
            request.owner, request.repo, request.issue_number
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
