from redforge.models import RiskLevel, VerificationReport
from redforge.production.models import RiskAssessment
from redforge.production.review import ReviewCoordinator


def test_review_consensus_passes_clean_change() -> None:
    result = ReviewCoordinator(required_approvals=2).review(
        VerificationReport(passed=True),
        RiskAssessment(score=0, level=RiskLevel.LOW),
        [],
    )
    assert result.approved
    assert result.approvals == 3
