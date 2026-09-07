from __future__ import annotations

from redforge.models import RiskLevel, VerificationReport
from redforge.production.models import (
    AgentVote,
    ConsensusResult,
    Decision,
    PolicyDecision,
    RiskAssessment,
)
from redforge.production.multi_agent import MultiAgentVerifier


class ReviewCoordinator:
    """Coordinates independent deterministic reviewer roles for the run gate."""

    def __init__(self, *, required_approvals: int = 2) -> None:
        self.verifier = MultiAgentVerifier(required_approvals=required_approvals)

    def review(
        self,
        verification: VerificationReport,
        risk: RiskAssessment,
        policy_decisions: list[PolicyDecision],
    ) -> ConsensusResult:
        blocking_security = any(
            finding.severity in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            and finding.source.lower() in {"security", "bandit", "semgrep"}
            for finding in verification.findings
        )
        policy_denied = any(decision.decision == Decision.DENY for decision in policy_decisions)

        votes = [
            AgentVote(
                agent="verification-reviewer",
                approved=verification.passed,
                confidence=1.0,
                reason=(
                    "Advanced verification passed."
                    if verification.passed
                    else "Advanced verification failed."
                ),
            ),
            AgentVote(
                agent="security-reviewer",
                approved=not blocking_security,
                confidence=0.95,
                reason=(
                    "No blocking security finding."
                    if not blocking_security
                    else "Blocking security finding detected."
                ),
            ),
            AgentVote(
                agent="risk-policy-reviewer",
                approved=not policy_denied and risk.level != RiskLevel.CRITICAL,
                confidence=0.9,
                reason=(
                    "Risk and policy gates are acceptable."
                    if not policy_denied and risk.level != RiskLevel.CRITICAL
                    else "Risk or policy gate blocks delivery."
                ),
            ),
        ]

        consensus = self.verifier.consensus(votes)

        # Verification failure and explicit policy denial are hard release blockers,
        # regardless of the numerical reviewer majority.
        if not verification.passed or policy_denied:
            return consensus.model_copy(update={"approved": False})

        return consensus
