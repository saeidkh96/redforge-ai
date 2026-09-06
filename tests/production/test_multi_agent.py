from redforge.production import AgentVote, MultiAgentVerifier


def test_requires_independent_majority() -> None:
    verifier = MultiAgentVerifier(required_approvals=2)
    result = verifier.consensus(
        [
            AgentVote(agent="reviewer-a", approved=True, confidence=0.9),
            AgentVote(agent="reviewer-b", approved=True, confidence=0.8),
            AgentVote(agent="reviewer-c", approved=False, confidence=0.7),
        ]
    )
    assert result.approved is True
    assert result.approvals == 2
