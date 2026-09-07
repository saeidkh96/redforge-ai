from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class RunStatus(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    PATCH_READY = "patch_ready"
    TESTED = "tested"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    REVIEWING = "reviewing"
    REVIEWED = "reviewed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERY_READY = "delivery_ready"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(BaseModel):
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    order: int
    title: str
    description: str
    target_files: list[str] = Field(default_factory=list)
    verification: list[str] = Field(default_factory=list)


class Plan(BaseModel):
    summary: str
    steps: list[PlanStep] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class Patch(BaseModel):
    diff: str
    rationale: str = ""
    files: list[str] = Field(default_factory=list)


class CommandResult(BaseModel):
    command: list[str]
    return_code: int
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return self.return_code == 0 and not self.timed_out


class TestRun(BaseModel):
    results: list[CommandResult] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(result.passed for result in self.results)


class RepairAttempt(BaseModel):
    attempt: int
    patch: Patch
    tests: TestRun
    applied: bool = False


class Finding(BaseModel):
    source: str
    severity: RiskLevel
    message: str
    path: str | None = None
    line: int | None = None
    rule_id: str | None = None


class VerificationReport(BaseModel):
    commands: list[CommandResult] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    passed: bool = False


class Approval(BaseModel):
    approved: bool = False
    required: bool = True
    risk: RiskLevel = RiskLevel.LOW
    reasons: list[str] = Field(default_factory=list)
    approver: str | None = None
    approved_at: datetime | None = None


class PullRequest(BaseModel):
    number: int | None = None
    url: str | None = None
    title: str
    body: str = ""
    head: str
    base: str = "main"


class ForgeRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: RunStatus = RunStatus.CREATED
    repository_path: str
    issue: Issue
    repository_summary: str | None = None
    plan: Plan | None = None
    patch: Patch | None = None
    tests: TestRun | None = None
    repair_attempts: list[RepairAttempt] = Field(default_factory=list)
    verification: VerificationReport | None = None
    policy_decisions: list[dict[str, Any]] = Field(default_factory=list)
    risk_assessment: dict[str, Any] | None = None
    review_consensus: dict[str, Any] | None = None
    runtime_evidence: dict[str, Any] | None = None
    approval: Approval | None = None
    pull_request: PullRequest | None = None
    delivery_ready: bool = False
    pending_action: str | None = None
    error: str | None = None
