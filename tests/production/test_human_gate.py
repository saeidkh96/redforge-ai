from redforge.models import Approval, ForgeRun, Issue, RiskLevel, RunStatus
from redforge.production.human_gate import HumanGate


def test_human_gate_approves_run() -> None:
    run = ForgeRun(
        repository_path=".",
        issue=Issue(title="test"),
        status=RunStatus.AWAITING_APPROVAL,
        approval=Approval(required=True, risk=RiskLevel.MEDIUM),
    )
    result = HumanGate().approve(run, actor="saeid", reason="reviewed")
    assert result.status == RunStatus.APPROVED
    assert result.approval is not None
    assert result.approval.approved
    assert result.approval.approver == "saeid"
