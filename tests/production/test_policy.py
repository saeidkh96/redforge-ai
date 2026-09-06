from pathlib import Path

from redforge.production import (
    AuthorizationEngine,
    Decision,
    Permission,
    Principal,
    RuntimeAction,
    RuntimePolicy,
)


def test_denies_workspace_escape(tmp_path: Path) -> None:
    policy = RuntimePolicy(workspace_root=tmp_path)
    engine = AuthorizationEngine(policy)
    principal = Principal(
        id="agent",
        permissions=[Permission.READ_REPOSITORY],
    )
    decision = engine.evaluate(
        principal,
        RuntimeAction(
            action="read",
            permission=Permission.READ_REPOSITORY,
            resource=str(tmp_path.parent),
        ),
    )
    assert decision.decision == Decision.DENY


def test_egress_allowlist(tmp_path: Path) -> None:
    policy = RuntimePolicy(
        workspace_root=tmp_path,
        allowed_egress_hosts={"api.github.com"},
    )
    engine = AuthorizationEngine(policy)
    principal = Principal(
        id="agent",
        permissions=[Permission.NETWORK_EGRESS],
    )
    allowed = engine.evaluate(
        principal,
        RuntimeAction(
            action="http",
            permission=Permission.NETWORK_EGRESS,
            resource="https://api.github.com/repos",
        ),
    )
    denied = engine.evaluate(
        principal,
        RuntimeAction(
            action="http",
            permission=Permission.NETWORK_EGRESS,
            resource="https://example.com",
        ),
    )
    assert allowed.decision == Decision.ALLOW
    assert denied.decision == Decision.DENY
