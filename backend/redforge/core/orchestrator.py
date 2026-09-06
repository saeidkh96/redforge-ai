from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from redforge.agents import CodingAgent, LLMProvider
from redforge.approval import ApprovalEngine
from redforge.execution import PatchEngine, RepairAgent, TestRunner
from redforge.models import ForgeRun, Issue, RepairAttempt, RunStatus
from redforge.persistence import RunStore
from redforge.planning import PlanningEngine
from redforge.repository import RepositoryScanner
from redforge.verification import VerificationEngine


class ForgeOrchestrator:
    def __init__(
        self,
        provider: LLMProvider | None = None,
        store: RunStore | None = None,
    ) -> None:
        self.provider = provider
        self.store = store or RunStore()

    def run(
        self,
        repository_path: str | Path,
        issue: Issue,
        *,
        generate_patch: bool = False,
        apply_patch: bool = False,
        repair_on_failure: bool = True,
        max_repair_attempts: int = 2,
    ) -> ForgeRun:
        if max_repair_attempts < 0:
            raise ValueError("max_repair_attempts must be greater than or equal to zero.")

        root = Path(repository_path).resolve()
        forge_run = ForgeRun(repository_path=str(root), issue=issue)

        try:
            snapshot = RepositoryScanner().scan(root)
            forge_run.repository_summary = snapshot.summary
            forge_run.plan = PlanningEngine().create_plan(issue, snapshot)
            forge_run.status = RunStatus.PLANNED

            if generate_patch:
                if self.provider is None:
                    raise RuntimeError("Patch generation requires an LLM provider.")

                forge_run.patch = CodingAgent(self.provider).propose_patch(
                    issue,
                    forge_run.plan,
                    snapshot,
                )
                forge_run.status = RunStatus.PATCH_READY
                PatchEngine().check(root, forge_run.patch)

                if apply_patch:
                    PatchEngine().apply(root, forge_run.patch)

            current_snapshot = RepositoryScanner().scan(root)
            forge_run.tests = TestRunner().run(root, current_snapshot)
            forge_run.status = RunStatus.TESTED

            self._repair_if_needed(
                root,
                forge_run,
                apply_patch=apply_patch,
                repair_on_failure=repair_on_failure,
                max_repair_attempts=max_repair_attempts,
            )

            forge_run.verification = VerificationEngine().verify(root)
            forge_run.status = RunStatus.VERIFIED
            forge_run.approval = ApprovalEngine().evaluate(
                forge_run.patch,
                forge_run.verification,
            )
            forge_run.status = (
                RunStatus.AWAITING_APPROVAL if forge_run.approval.required else RunStatus.COMPLETED
            )
        except Exception as exc:
            forge_run.status = RunStatus.FAILED
            forge_run.error = str(exc)
        finally:
            forge_run.updated_at = datetime.now(UTC)
            self.store.save(forge_run)

        return forge_run

    def _repair_if_needed(
        self,
        root: Path,
        forge_run: ForgeRun,
        *,
        apply_patch: bool,
        repair_on_failure: bool,
        max_repair_attempts: int,
    ) -> None:
        if forge_run.tests is None or forge_run.tests.passed:
            return
        if not repair_on_failure or max_repair_attempts == 0:
            return
        if not apply_patch or forge_run.patch is None or self.provider is None:
            return

        repair_agent = RepairAgent(self.provider)
        previous_patch = forge_run.patch

        for attempt_number in range(1, max_repair_attempts + 1):
            if forge_run.tests is None or forge_run.tests.passed:
                break

            forge_run.status = RunStatus.REPAIRING
            repair_patch = repair_agent.propose_repair(
                previous_patch,
                forge_run.tests,
                attempt=attempt_number,
            )
            PatchEngine().check(root, repair_patch)
            PatchEngine().apply(root, repair_patch)

            snapshot = RepositoryScanner().scan(root)
            repaired_tests = TestRunner().run(root, snapshot)
            forge_run.repair_attempts.append(
                RepairAttempt(
                    attempt=attempt_number,
                    patch=repair_patch,
                    tests=repaired_tests,
                    applied=True,
                )
            )
            forge_run.tests = repaired_tests
            forge_run.status = RunStatus.REPAIRED
            previous_patch = repair_patch
