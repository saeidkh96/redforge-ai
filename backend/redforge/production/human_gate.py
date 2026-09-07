from __future__ import annotations

from datetime import UTC, datetime

from redforge.models import Approval, ForgeRun, RiskLevel, RunStatus
from redforge.production.audit import HashChainAuditLog


class HumanGate:
    """Applies and optionally audits a human decision for a ForgeRun."""

    def __init__(self, audit: HashChainAuditLog | None = None) -> None:
        self.audit = audit

    def approve(self, run: ForgeRun, *, actor: str, reason: str = "") -> ForgeRun:
        existing = run.approval or Approval(required=True, risk=RiskLevel.MEDIUM)
        reasons = list(existing.reasons)
        if reason:
            reasons.append(reason)

        run.approval = existing.model_copy(
            update={
                "approved": True,
                "required": True,
                "approver": actor,
                "approved_at": datetime.now(UTC),
                "reasons": reasons,
            }
        )
        run.status = RunStatus.APPROVED

        if self.audit is not None:
            self.audit.append(
                event_type="human_decision",
                actor=actor,
                action="approve_run",
                resource=run.id,
                payload={
                    "approved": True,
                    "reason": reason,
                    "risk": run.approval.risk,
                    "pending_action": run.pending_action,
                },
            )

        return run

    def reject(self, run: ForgeRun, *, actor: str, reason: str) -> ForgeRun:
        existing = run.approval or Approval(required=True, risk=RiskLevel.MEDIUM)
        reasons = list(existing.reasons)
        reasons.append(reason)

        run.approval = existing.model_copy(
            update={
                "approved": False,
                "required": True,
                "approver": actor,
                "approved_at": datetime.now(UTC),
                "reasons": reasons,
            }
        )
        run.status = RunStatus.REJECTED

        if self.audit is not None:
            self.audit.append(
                event_type="human_decision",
                actor=actor,
                action="reject_run",
                resource=run.id,
                payload={
                    "approved": False,
                    "reason": reason,
                    "risk": run.approval.risk,
                    "pending_action": run.pending_action,
                },
            )

        return run
