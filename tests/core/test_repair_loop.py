from pathlib import Path
from unittest.mock import MagicMock, patch

from redforge.agents import StaticProvider
from redforge.core.orchestrator import ForgeOrchestrator
from redforge.models import CommandResult, Patch
from redforge.models import TestRun as ForgeTestRun


def _test_run(return_code: int) -> ForgeTestRun:
    return ForgeTestRun(
        results=[
            CommandResult(
                command=["python", "-m", "pytest", "-q"],
                return_code=return_code,
            )
        ]
    )


def test_repair_loop_stops_after_tests_pass(tmp_path: Path) -> None:
    run = MagicMock()
    run.tests = _test_run(1)
    run.patch = Patch(diff="initial", files=["a.py"])
    run.repair_attempts = []

    provider = StaticProvider("{}")
    orchestrator = ForgeOrchestrator(provider=provider)
    repair_patch = Patch(diff="repair", files=["a.py"])

    with (
        patch("redforge.core.orchestrator.RepairAgent.propose_repair", return_value=repair_patch),
        patch("redforge.core.orchestrator.PatchEngine.check"),
        patch("redforge.core.orchestrator.PatchEngine.apply"),
        patch("redforge.core.orchestrator.RepositoryScanner.scan"),
        patch("redforge.core.orchestrator.TestRunner.run", return_value=_test_run(0)),
    ):
        orchestrator._repair_if_needed(
            tmp_path,
            run,
            apply_patch=True,
            repair_on_failure=True,
            max_repair_attempts=3,
        )

    assert run.tests.passed is True
    assert len(run.repair_attempts) == 1
    assert run.repair_attempts[0].attempt == 1
    assert run.repair_attempts[0].applied is True
