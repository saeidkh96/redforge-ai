from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class AgentKind(StrEnum):
    PLANNER = "planner"
    CODER = "coder"
    REPAIR = "repair"
    REVIEWER = "reviewer"
    VERIFIER = "verifier"


class AgentResult(BaseModel):
    agent: AgentKind
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SymbolRecord(BaseModel):
    path: str
    name: str
    kind: str
    line: int | None = None
    qualified_name: str | None = None


class DependencyRecord(BaseModel):
    source: str
    target: str
    kind: str


class CallRecord(BaseModel):
    source_path: str
    source_symbol: str
    target_symbol: str
    line: int | None = None


class DeepImpactReport(BaseModel):
    changed_files: list[str] = Field(default_factory=list)
    directly_impacted: list[str] = Field(default_factory=list)
    transitively_impacted: list[str] = Field(default_factory=list)
    suggested_tests: list[str] = Field(default_factory=list)
    dependencies: list[DependencyRecord] = Field(default_factory=list)
    symbols: list[SymbolRecord] = Field(default_factory=list)
    calls: list[CallRecord] = Field(default_factory=list)
    changed_symbols: list[str] = Field(default_factory=list)
    impacted_symbols: list[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)


class BenchmarkCase(BaseModel):
    name: str
    expected_success: bool = True
    expected_delivery_ready: bool | None = None
    category: str = "general"


class BenchmarkObservation(BaseModel):
    name: str
    expected_success: bool
    actual_success: bool
    expected_delivery_ready: bool | None = None
    actual_delivery_ready: bool | None = None
    passed: bool
    category: str = "general"


class ReliabilityMetrics(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    success_rate: float = 0.0
    true_positive: int = 0
    true_negative: int = 0
    false_positive: int = 0
    false_negative: int = 0
    precision: float = 0.0
    recall: float = 0.0
    accuracy: float = 0.0
    f1: float = 0.0


class HardeningProfile(BaseModel):
    require_verification: bool = True
    require_review_consensus: bool = True
    require_audit_evidence: bool = True
    require_human_approval_when_requested: bool = True
    require_integrity_evidence: bool = True
    redact_secrets: bool = True


class ReleaseGate(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    evidence_hash: str | None = None


class GitHubIssueSpec(BaseModel):
    owner: str
    repo: str
    issue_number: int = Field(ge=1)
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    html_url: str | None = None
    sender: str | None = None


class GitHubWebhookEvent(BaseModel):
    delivery_id: str
    action: str
    issue: GitHubIssueSpec


class AutonomousRunReport(BaseModel):
    run_id: str
    status: str
    delivery_ready: bool = False
    branch: str | None = None
    pull_request_url: str | None = None
    impact: DeepImpactReport | None = None
    gate: ReleaseGate | None = None
    reliability: ReliabilityMetrics | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
