from redforge.models import ForgeRun, Issue


def test_forge_run_has_v130_evidence_fields() -> None:
    run = ForgeRun(repository_path=".", issue=Issue(title="test"))
    assert run.policy_decisions == []
    assert run.risk_assessment is None
    assert run.review_consensus is None
    assert run.runtime_evidence is None
    assert run.delivery_ready is False
