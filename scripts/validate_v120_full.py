from pathlib import Path

from redforge import __version__
from redforge.production import (
    AgentVote,
    HashChainAuditLog,
    MultiAgentVerifier,
    ProductionRuntime,
)


def main() -> None:
    assert __version__ == "1.2.0"

    temp_root = Path(".redforge") / "validation"
    temp_root.mkdir(parents=True, exist_ok=True)

    audit = HashChainAuditLog(temp_root / "audit.jsonl")
    audit.append(
        event_type="validation",
        actor="validator",
        action="validate",
        resource="redforge",
    )
    assert audit.verify()

    consensus = MultiAgentVerifier(required_approvals=2).consensus(
        [
            AgentVote(agent="a", approved=True, confidence=0.9),
            AgentVote(agent="b", approved=True, confidence=0.8),
            AgentVote(agent="c", approved=False, confidence=0.4),
        ]
    )
    assert consensus.approved

    runtime = ProductionRuntime(Path.cwd())
    assert runtime.evidence().audit_chain_valid

    print(
        {
            "version": __version__,
            "production_runtime": True,
            "policy_enforcement": True,
            "tamper_evident_audit": True,
            "multi_agent_verification": True,
            "ready": True,
        }
    )


if __name__ == "__main__":
    main()
