from __future__ import annotations

from redforge.production.models import AgentVote, ConsensusResult


class MultiAgentVerifier:
    def __init__(self, *, required_approvals: int = 2) -> None:
        if required_approvals < 1:
            raise ValueError("required_approvals must be at least 1.")
        self.required_approvals = required_approvals

    def consensus(self, votes: list[AgentVote]) -> ConsensusResult:
        approvals = sum(v.approved for v in votes)
        rejections = len(votes) - approvals

        total_weight = sum(max(v.confidence, 0.0) for v in votes)
        approval_weight = sum(max(v.confidence, 0.0) for v in votes if v.approved)
        confidence = approval_weight / total_weight if total_weight else 0.0

        approved = (
            approvals >= self.required_approvals and approvals > rejections and confidence >= 0.5
        )
        return ConsensusResult(
            approved=approved,
            approvals=approvals,
            rejections=rejections,
            confidence=confidence,
            votes=votes,
        )
