from redforge.approval import ApprovalEngine
from redforge.models import Patch, VerificationReport


def test_sensitive_patch_requires_approval() -> None:
    approval = ApprovalEngine().evaluate(
        Patch(diff="", files=["backend/auth/service.py"]),
        VerificationReport(passed=True),
    )
    assert approval.required is True
    assert approval.risk == "high"
