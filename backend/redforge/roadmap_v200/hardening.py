from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from redforge.roadmap_v200.models import HardeningProfile, ReleaseGate


class SecretRedactor:
    _PATTERNS = (
        re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([^\s,;]+)"),
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    )

    def redact(self, value: str) -> str:
        output = value
        for pattern in self._PATTERNS:
            output = pattern.sub(self._replace, output)
        return output

    @staticmethod
    def _replace(match: re.Match[str]) -> str:
        if match.lastindex and match.lastindex >= 2:
            return f"{match.group(1)}=[REDACTED]"
        return "[REDACTED]"


class WorkspaceBoundary:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def require_inside(self, candidate: str | Path) -> Path:
        resolved = Path(candidate).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError(f"Path escapes workspace: {resolved}") from exc
        return resolved


class ReleaseGateEvaluator:
    def __init__(self, profile: HardeningProfile | None = None) -> None:
        self.profile = profile or HardeningProfile()

    def evaluate(self, evidence: dict[str, Any]) -> ReleaseGate:
        reasons: list[str] = []
        if self.profile.require_verification and not bool(evidence.get("verification_passed")):
            reasons.append("Verification has not passed.")
        if self.profile.require_review_consensus and not bool(evidence.get("review_approved")):
            reasons.append("Review consensus has not approved delivery.")
        if self.profile.require_audit_evidence and not bool(evidence.get("audit_present")):
            reasons.append("Audit evidence is missing.")
        approval_required = bool(evidence.get("human_approval_required"))
        approval_granted = bool(evidence.get("human_approval_granted"))
        if (
            self.profile.require_human_approval_when_requested
            and approval_required
            and not approval_granted
        ):
            reasons.append("Required human approval is missing.")
        return ReleaseGate(passed=not reasons, reasons=reasons)
