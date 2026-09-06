from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class Permission(StrEnum):
    READ_REPOSITORY = "read_repository"
    WRITE_REPOSITORY = "write_repository"
    EXECUTE_COMMAND = "execute_command"
    NETWORK_EGRESS = "network_egress"
    CREATE_BRANCH = "create_branch"
    CREATE_COMMIT = "create_commit"
    CREATE_PULL_REQUEST = "create_pull_request"
    APPROVE_RUN = "approve_run"


class Principal(BaseModel):
    id: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[Permission] = Field(default_factory=list)


class RuntimeAction(BaseModel):
    action: str
    permission: Permission
    resource: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseModel):
    decision: Decision
    reason: str
    policy_id: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditEvent(BaseModel):
    sequence: int
    timestamp: datetime
    event_type: str
    actor: str
    action: str
    resource: str
    payload: dict[str, Any] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str


class ReviewerOutcome(BaseModel):
    reviewer: str
    expected_safe: bool
    predicted_safe: bool


class ReviewerScore(BaseModel):
    reviewer: str
    true_positive: int = 0
    true_negative: int = 0
    false_positive: int = 0
    false_negative: int = 0
    precision: float = 0.0
    recall: float = 0.0
    accuracy: float = 0.0
    reliability: float = 0.0


class AgentVote(BaseModel):
    agent: str
    approved: bool
    confidence: float = 1.0
    reason: str = ""


class ConsensusResult(BaseModel):
    approved: bool
    approvals: int
    rejections: int
    confidence: float
    votes: list[AgentVote] = Field(default_factory=list)


class RuntimeEvidence(BaseModel):
    audit_chain_valid: bool = True
    policy_decisions: list[PolicyDecision] = Field(default_factory=list)
    reviewer_scores: list[ReviewerScore] = Field(default_factory=list)
    consensus: ConsensusResult | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
