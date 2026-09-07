from __future__ import annotations

from redforge.models import Patch, RiskLevel, VerificationReport
from redforge.production.models import PolicyDecision, RiskAssessment


class RiskEngine:
    """Deterministic change-risk scoring used by the v1.3.0 run gate."""

    SENSITIVE_TOKENS = (
        ".github/",
        "infra/",
        "migrations/",
        "auth/",
        "security/",
        "payment/",
        "secrets/",
    )

    def evaluate(
        self,
        patch: Patch | None,
        verification: VerificationReport,
        policy_decisions: list[PolicyDecision],
    ) -> RiskAssessment:
        score = 0.0
        reasons: list[str] = []
        files = patch.files if patch else []

        if len(files) > 8:
            score += 20.0
            reasons.append("Patch changes more than eight files.")
        elif len(files) > 3:
            score += 10.0
            reasons.append("Patch changes multiple files.")

        normalized_files = [path.replace("\\", "/").lower() for path in files]
        if any(token in path for path in normalized_files for token in self.SENSITIVE_TOKENS):
            score += 35.0
            reasons.append("Patch touches a sensitive repository area.")

        high_findings = sum(finding.severity == RiskLevel.HIGH for finding in verification.findings)
        critical_findings = sum(
            finding.severity == RiskLevel.CRITICAL for finding in verification.findings
        )
        if high_findings:
            score += min(30.0, high_findings * 10.0)
            reasons.append(f"Verification reported {high_findings} high-severity finding(s).")
        if critical_findings:
            score += 40.0
            reasons.append(f"Verification reported {critical_findings} critical finding(s).")
        if not verification.passed:
            score += 25.0
            reasons.append("Verification did not pass.")

        approval_decisions = sum(
            decision.decision == "require_approval" for decision in policy_decisions
        )
        denied_decisions = sum(decision.decision == "deny" for decision in policy_decisions)
        if approval_decisions:
            score += min(20.0, approval_decisions * 10.0)
            reasons.append("Runtime policy requires human approval.")
        if denied_decisions:
            score += 50.0
            reasons.append("Runtime policy denied at least one action.")

        score = min(score, 100.0)
        if score >= 80:
            level = RiskLevel.CRITICAL
        elif score >= 50:
            level = RiskLevel.HIGH
        elif score >= 20:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return RiskAssessment(score=score, level=level, reasons=reasons)
