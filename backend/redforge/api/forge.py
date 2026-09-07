from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, SecretStr

from redforge.agents import OpenAICompatibleProvider
from redforge.core.config import get_settings
from redforge.core.orchestrator import ForgeOrchestrator
from redforge.models import ForgeRun, Issue, RunStatus
from redforge.persistence import RunStore
from redforge.production.github_workflow import GitHubWorkflow
from redforge.production.human_gate import HumanGate
from redforge.production.runtime import ProductionRuntime

router = APIRouter(prefix="/api/v1/forge", tags=["forge"])


class ForgeRunRequest(BaseModel):
    repository_path: str
    issue: Issue
    generate_patch: bool = False
    apply_patch: bool = False
    repair_on_failure: bool | None = None
    max_repair_attempts: int | None = Field(default=None, ge=0, le=10)
    use_production_runtime: bool | None = None


class HumanDecisionRequest(BaseModel):
    actor: str = Field(min_length=1)
    reason: str = ""


class PublishRunRequest(BaseModel):
    actor: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    token: SecretStr
    branch: str | None = None
    commit_message: str | None = None
    title: str | None = None
    body: str = ""
    base_branch: str = "main"
    remote: str = "origin"
    create_pr: bool = True


def _provider() -> OpenAICompatibleProvider | None:
    settings = get_settings()
    if not settings.llm_base_url or not settings.llm_model:
        return None

    return OpenAICompatibleProvider(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
    )


def _runtime_for_run(run: ForgeRun, *, actor: str) -> ProductionRuntime:
    settings = get_settings()

    return ProductionRuntime(
        Path(run.repository_path),
        actor=actor,
        allowed_egress_hosts=settings.egress_host_set,
        audit_path=settings.audit_log_path,
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
        use_production_runtime=request.use_production_runtime,
    )


def _load_run(run_id: str) -> tuple[RunStore, ForgeRun]:
    store = RunStore()

    try:
        return store, store.load(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="ForgeRun not found") from exc


@router.post("/runs/{run_id}/approve", response_model=ForgeRun)
def approve_forge_run(run_id: str, request: HumanDecisionRequest) -> ForgeRun:
    store, run = _load_run(run_id)

    if run.status != RunStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=409,
            detail="ForgeRun is not awaiting approval",
        )

    runtime = _runtime_for_run(run, actor=request.actor)
    run = HumanGate(runtime.audit).approve(
        run,
        actor=request.actor,
        reason=request.reason,
    )
    store.save(run)

    if run.pending_action == "apply_patch":
        settings = get_settings()
        return ForgeOrchestrator(
            provider=_provider(),
            store=store,
        ).resume_after_approval(
            run,
            repair_on_failure=settings.repair_on_failure,
            max_repair_attempts=settings.max_repair_attempts,
            use_production_runtime=True,
        )

    if (
        run.verification is not None
        and run.verification.passed
        and run.review_consensus is not None
        and bool(run.review_consensus.get("approved"))
    ):
        run.delivery_ready = True
        run.status = RunStatus.DELIVERY_READY

    store.save(run)
    return run


@router.post("/runs/{run_id}/reject", response_model=ForgeRun)
def reject_forge_run(run_id: str, request: HumanDecisionRequest) -> ForgeRun:
    if not request.reason.strip():
        raise HTTPException(
            status_code=400,
            detail="A rejection reason is required",
        )

    store, run = _load_run(run_id)

    if run.status != RunStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=409,
            detail="ForgeRun is not awaiting approval",
        )

    runtime = _runtime_for_run(run, actor=request.actor)
    run = HumanGate(runtime.audit).reject(
        run,
        actor=request.actor,
        reason=request.reason,
    )

    store.save(run)
    return run


@router.post("/runs/{run_id}/publish", response_model=ForgeRun)
def publish_forge_run(run_id: str, request: PublishRunRequest) -> ForgeRun:
    store, run = _load_run(run_id)

    if run.status != RunStatus.DELIVERY_READY or not run.delivery_ready:
        raise HTTPException(
            status_code=409,
            detail="ForgeRun is not delivery-ready",
        )

    if run.verification is None or not run.verification.passed:
        raise HTTPException(
            status_code=409,
            detail="ForgeRun verification has not passed",
        )

    if run.review_consensus is None or not bool(run.review_consensus.get("approved")):
        raise HTTPException(
            status_code=409,
            detail="ForgeRun review consensus has not approved delivery",
        )

    if run.approval is not None and run.approval.required and not run.approval.approved:
        raise HTTPException(
            status_code=409,
            detail="Required human approval is missing",
        )

    branch = request.branch or f"redforge/run-{run.id[:8]}"
    commit_message = request.commit_message or f"feat: apply RedForge run {run.id[:8]}"
    title = request.title or run.issue.title

    runtime = _runtime_for_run(run, actor=request.actor)

    try:
        result = GitHubWorkflow(
            owner=request.owner,
            repo=request.repo,
            token=request.token.get_secret_value(),
            base_branch=request.base_branch,
        ).publish(
            run.repository_path,
            branch=branch,
            commit_message=commit_message,
            title=title,
            body=request.body,
            create_pr=request.create_pr,
            remote=request.remote,
            runtime=runtime,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    run.pull_request = result.pull_request
    run.status = RunStatus.COMPLETED

    runtime.record_delivery(
        run_id=run.id,
        branch=result.branch,
        pull_request_url=result.pull_request.url if result.pull_request else None,
    )

    evidence = runtime.evidence().model_dump(mode="json")
    evidence["consensus"] = run.review_consensus
    run.runtime_evidence = evidence

    store.save(run)
    return run
