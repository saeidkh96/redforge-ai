from __future__ import annotations

from pathlib import Path

from redforge.models import VerificationReport
from redforge.production.audit import HashChainAuditLog
from redforge.production.models import (
    Decision,
    Permission,
    PolicyDecision,
    Principal,
    RuntimeAction,
    RuntimeEvidence,
)
from redforge.production.observability import MetricsRegistry
from redforge.production.policy import AuthorizationEngine, RuntimePolicy
from redforge.production.sandbox import SandboxedCommandRunner
from redforge.verification.advanced import (
    AdvancedVerificationEngine,
    VerificationProfile,
)


class ProductionRuntime:
    """Unified enforcement boundary for RedForge autonomous actions."""

    def __init__(
        self,
        workspace_root: str | Path,
        *,
        actor: str = "redforge-agent",
        allowed_egress_hosts: set[str] | None = None,
        audit_path: str | Path | None = None,
    ) -> None:
        root = Path(workspace_root).resolve()
        self.root = root
        self.metrics = MetricsRegistry()
        self.policy = RuntimePolicy(
            workspace_root=root,
            allowed_egress_hosts=allowed_egress_hosts or set(),
        )
        self.authorization = AuthorizationEngine(self.policy)
        self.principal = Principal(
            id=actor,
            roles=["software_engineering_agent"],
            permissions=[
                Permission.READ_REPOSITORY,
                Permission.WRITE_REPOSITORY,
                Permission.EXECUTE_COMMAND,
                Permission.CREATE_BRANCH,
                Permission.CREATE_COMMIT,
                Permission.CREATE_PULL_REQUEST,
            ],
        )
        self.audit = HashChainAuditLog(audit_path or root / ".redforge" / "audit" / "events.jsonl")
        self.runner = SandboxedCommandRunner(self.authorization, self.principal)

    def authorize(self, action: RuntimeAction) -> PolicyDecision:
        decision = self.authorization.evaluate(self.principal, action)
        self.audit.append(
            event_type="policy_decision",
            actor=self.principal.id,
            action=action.action,
            resource=action.resource,
            payload={
                "decision": decision.decision,
                "reason": decision.reason,
                "policy_id": decision.policy_id,
            },
        )
        self.metrics.increment(f"policy_{decision.decision}")
        return decision

    def verify_repository(
        self,
        profile: VerificationProfile | None = None,
    ) -> VerificationReport:
        self.audit.append(
            event_type="verification_started",
            actor=self.principal.id,
            action="verify_repository",
            resource=str(self.root),
        )
        with self.metrics.timer("verification"):
            report = AdvancedVerificationEngine(
                self.runner,
                profile=profile,
            ).verify(self.root)

        self.audit.append(
            event_type="verification_completed",
            actor=self.principal.id,
            action="verify_repository",
            resource=str(self.root),
            payload={
                "passed": report.passed,
                "findings": len(report.findings),
                "commands": len(report.commands),
            },
        )
        return report

    def evidence(self) -> RuntimeEvidence:
        return RuntimeEvidence(
            audit_chain_valid=self.audit.verify(),
            metrics=self.metrics.snapshot(),
        )

    def require_allowed(self, action: RuntimeAction) -> None:
        decision = self.authorize(action)
        if decision.decision == Decision.DENY:
            raise PermissionError(decision.reason)
        if decision.decision == Decision.REQUIRE_APPROVAL:
            raise PermissionError(f"Human approval required before action: {decision.reason}")
