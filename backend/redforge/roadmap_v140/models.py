from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class NodeStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WAITING = "waiting"
    SKIPPED = "skipped"


class ExecutionMode(StrEnum):
    HOST = "host"
    DOCKER = "docker"


class AgentRole(StrEnum):
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    REPAIR = "repair"
    VERIFIER = "verifier"


class AgentMessage(BaseModel):
    role: AgentRole
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeRecord(BaseModel):
    name: str
    status: NodeStatus = NodeStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None
    attempts: int = 0
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class GraphCheckpoint(BaseModel):
    run_id: str
    current_node: str | None = None
    records: dict[str, NodeRecord] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    completed: bool = False
    failed: bool = False


class SandboxLimits(BaseModel):
    cpus: float = Field(default=1.0, gt=0)
    memory_mb: int = Field(default=1024, ge=128)
    timeout_seconds: int = Field(default=300, ge=1)
    network_enabled: bool = False
    read_only_root: bool = True


class SandboxResult(BaseModel):
    command: list[str]
    return_code: int
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    timed_out: bool = False
    mode: ExecutionMode = ExecutionMode.DOCKER


class DependencyEdge(BaseModel):
    source: str
    target: str
    kind: str = "import"


class ImpactReport(BaseModel):
    changed_files: list[str] = Field(default_factory=list)
    directly_impacted: list[str] = Field(default_factory=list)
    transitively_impacted: list[str] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0.0, le=100.0)


class ProviderUsage(BaseModel):
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_seconds: float = 0.0


class MemoryRecord(BaseModel):
    key: str
    namespace: str = "default"
    value: dict[str, Any]
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class GitHubIssueEvent(BaseModel):
    owner: str
    repo: str
    issue_number: int = Field(ge=1)
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    sender: str | None = None


class AutonomyResult(BaseModel):
    run_id: str
    checkpoint: GraphCheckpoint
    delivery_ready: bool = False
    branch: str | None = None
    pull_request_url: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
