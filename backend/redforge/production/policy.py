from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from redforge.production.models import (
    Decision,
    Permission,
    PolicyDecision,
    Principal,
    RuntimeAction,
)


@dataclass(slots=True)
class RuntimePolicy:
    workspace_root: Path
    allowed_commands: set[str] = field(
        default_factory=lambda: {
            "python",
            "python.exe",
            "pytest",
            "ruff",
            "mypy",
            "git",
            "npm",
            "node",
            "cargo",
            "go",
        }
    )
    allowed_egress_hosts: set[str] = field(default_factory=set)
    sensitive_paths: tuple[str, ...] = (
        ".github/",
        "infra/",
        "migrations/",
        "auth/",
        "security/",
        "payment/",
        "secrets/",
    )

    def normalize_resource(self, resource: str) -> Path:
        value = Path(resource)
        if not value.is_absolute():
            value = self.workspace_root / value
        return value.resolve()

    def resource_inside_workspace(self, resource: str) -> bool:
        try:
            self.normalize_resource(resource).relative_to(self.workspace_root.resolve())
            return True
        except ValueError:
            return False


class AuthorizationEngine:
    def __init__(self, policy: RuntimePolicy) -> None:
        self.policy = policy

    def evaluate(self, principal: Principal, action: RuntimeAction) -> PolicyDecision:
        if action.permission not in principal.permissions:
            return PolicyDecision(
                decision=Decision.DENY,
                reason=f"Principal lacks permission: {action.permission}",
                policy_id="permission.required",
            )

        if action.permission in {
            Permission.READ_REPOSITORY,
            Permission.WRITE_REPOSITORY,
            Permission.EXECUTE_COMMAND,
        }:
            resource = action.resource or str(self.policy.workspace_root)
            if not self.policy.resource_inside_workspace(resource):
                return PolicyDecision(
                    decision=Decision.DENY,
                    reason="Resource escapes configured workspace boundary.",
                    policy_id="workspace.boundary",
                )

        if action.permission == Permission.EXECUTE_COMMAND:
            command = str(action.metadata.get("command", "")).strip()
            executable = Path(command.split()[0]).name.lower() if command else ""
            if executable not in {item.lower() for item in self.policy.allowed_commands}:
                return PolicyDecision(
                    decision=Decision.DENY,
                    reason=f"Command is not allow-listed: {executable}",
                    policy_id="command.allowlist",
                )

        if action.permission == Permission.NETWORK_EGRESS:
            host = urlparse(action.resource).hostname or action.resource
            if host not in self.policy.allowed_egress_hosts:
                return PolicyDecision(
                    decision=Decision.DENY,
                    reason=f"Egress destination is not allow-listed: {host}",
                    policy_id="egress.allowlist",
                )

        normalized = action.resource.replace("\\", "/").lower()
        if any(token in normalized for token in self.policy.sensitive_paths):
            return PolicyDecision(
                decision=Decision.REQUIRE_APPROVAL,
                reason="Sensitive resource requires human approval.",
                policy_id="sensitive.human_gate",
            )

        return PolicyDecision(
            decision=Decision.ALLOW,
            reason="Action permitted by runtime policy.",
            policy_id="default.allow",
        )
