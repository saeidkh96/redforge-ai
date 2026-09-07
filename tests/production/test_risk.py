from redforge.models import Patch, RiskLevel, VerificationReport
from redforge.production.risk import RiskEngine


def test_sensitive_patch_increases_risk() -> None:
    assessment = RiskEngine().evaluate(
        Patch(diff="", files=["auth/session.py"]),
        VerificationReport(passed=True),
        [],
    )
    assert assessment.score >= 20
    assert assessment.level in {RiskLevel.MEDIUM, RiskLevel.HIGH}
