from redforge.models import Approval, Patch, RiskLevel, VerificationReport


class ApprovalEngine:
    def evaluate(self, patch: Patch | None, verification: VerificationReport) -> Approval:
        reasons: list[str] = []
        risk = RiskLevel.LOW
        files = patch.files if patch else []
        sensitive_tokens = ("auth", "security", "payment", "migration", "infra/", ".github/")
        if any(any(token in path.lower() for token in sensitive_tokens) for path in files):
            risk = RiskLevel.HIGH
            reasons.append("Patch touches a sensitive area.")
        elif len(files) > 8:
            risk = RiskLevel.MEDIUM
            reasons.append("Patch changes many files.")
        for finding in verification.findings:
            if finding.severity == RiskLevel.CRITICAL:
                risk = RiskLevel.CRITICAL
            elif finding.severity == RiskLevel.HIGH and risk != RiskLevel.CRITICAL:
                risk = RiskLevel.HIGH
        if not verification.passed:
            reasons.append("Verification did not pass.")
        required = risk != RiskLevel.LOW or not verification.passed
        return Approval(approved=False, required=required, risk=risk, reasons=reasons)
