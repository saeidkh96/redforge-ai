from pathlib import Path

import pytest
from redforge.models import Approval, ForgeRun, Issue, RunStatus, VerificationReport
from redforge.roadmap_v200 import IntegratedAutonomyRuntime


def test_integrated_runtime_records_checkpoint_and_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(self: object, repository_path: Path, issue: Issue, **kwargs: object) -> ForgeRun:
        return ForgeRun(
            repository_path=str(repository_path),
            issue=issue,
            status=RunStatus.DELIVERY_READY,
            verification=VerificationReport(passed=True),
            review_consensus={"approved": True},
            runtime_evidence={"audit_chain_valid": True},
            approval=Approval(approved=True, required=False),
            delivery_ready=True,
        )

    monkeypatch.setattr("redforge.roadmap_v200.runtime.ForgeOrchestrator.run", fake_run)
    runtime = IntegratedAutonomyRuntime(tmp_path, docker_probe=False)
    report = runtime.run_issue(Issue(title="test"))

    assert report.delivery_ready
    assert report.gate is not None and report.gate.passed
    assert runtime.checkpoints.exists(report.evidence["checkpoint_run_id"])
    assert runtime.memory.get(f"forge-run:{report.run_id}", namespace="v2-runs")
