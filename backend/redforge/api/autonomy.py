from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr

from redforge.core.config import get_settings
from redforge.roadmap_v140 import GitHubAutonomyPlanner, GitHubIssueEvent, PythonImpactAnalyzer
from redforge.roadmap_v200 import DeepRepositoryAnalyzer, GitHubIssueClient, GitHubIssueSpec
from redforge.roadmap_v200.github_live import GitHubAutonomyRunner
from redforge.roadmap_v200.webhook import (
    GitHubWebhookParser,
    GitHubWebhookVerifier,
    WebhookDeliveryStore,
)

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


class GitHubIssueRunRequest(GitHubIssueFetchRequest):
    workspace_root: str
    generate_patch: bool = True
    apply_patch: bool = True
    publish: bool = False


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


@router.post("/github-issue/run")
def run_github_issue(request: GitHubIssueRunRequest) -> dict[str, Any]:
    try:
        report = GitHubAutonomyRunner(
            token=request.token.get_secret_value(),
            workspace_root=request.workspace_root,
        ).run(
            request.owner,
            request.repo,
            request.issue_number,
            generate_patch=request.generate_patch,
            apply_patch=request.apply_patch,
            publish=request.publish,
        )
        return report.model_dump(mode="json")
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/github/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = get_settings()
    if x_github_event != "issues":
        return {"accepted": False, "reason": "unsupported_event"}
    if not settings.github_webhook_secret:
        raise HTTPException(status_code=503, detail="GitHub webhook secret is not configured.")
    body = await request.body()
    if not GitHubWebhookVerifier(settings.github_webhook_secret).verify(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature.")
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Delivery header.")

    event = GitHubWebhookParser().parse(body, x_github_delivery)
    if settings.github_automation_label not in event.issue.labels:
        return {"accepted": False, "reason": "missing_automation_label"}

    workspace_root = Path(settings.workspace_root or ".redforge/workspaces").resolve()
    delivery_store = WebhookDeliveryStore(
        workspace_root / ".redforge" / "github-deliveries.sqlite3"
    )
    if not delivery_store.claim(event.delivery_id):
        return {"accepted": False, "reason": "duplicate_delivery"}

    response: dict[str, Any] = {
        "accepted": True,
        "delivery_id": event.delivery_id,
        "issue": event.issue.model_dump(mode="json"),
    }
    if settings.github_live_automation_enabled:
        if not settings.github_token:
            raise HTTPException(status_code=503, detail="GitHub token is not configured.")
        report = GitHubAutonomyRunner(
            token=settings.github_token,
            workspace_root=workspace_root,
        ).run_spec(
            event.issue,
            generate_patch=True,
            apply_patch=True,
            publish=settings.github_auto_publish_enabled,
            comment_status=True,
        )
        response["report"] = report.model_dump(mode="json")
    return response
