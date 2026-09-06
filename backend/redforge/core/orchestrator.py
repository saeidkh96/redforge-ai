from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from redforge.agents import CodingAgent, LLMProvider
from redforge.approval import ApprovalEngine
from redforge.execution import PatchEngine, TestRunner
from redforge.models import ForgeRun, Issue, RunStatus
from redforge.persistence import RunStore
from redforge.planning import PlanningEngine
from redforge.repository import RepositoryScanner
from redforge.verification import VerificationEngine


class ForgeOrchestrator:
    def __init__(self, provider: LLMProvider | None = None, store: RunStore | None = None) -> None:
        self.provider = provider
        self.store = store or RunStore()

    def run(
        self,
        repository_path: str | Path,
        issue: Issue,
        *,
        generate_patch: bool = False,
        apply_patch: bool = False,
    ) -> ForgeRun:
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
                    issue, forge_run.plan, snapshot
                )
                forge_run.status = RunStatus.PATCH_READY
                PatchEngine().check(root, forge_run.patch)
                if apply_patch:
                    PatchEngine().apply(root, forge_run.patch)

            current_snapshot = RepositoryScanner().scan(root)
            forge_run.tests = TestRunner().run(root, current_snapshot)
            forge_run.status = RunStatus.TESTED
            forge_run.verification = VerificationEngine().verify(root)
            forge_run.status = RunStatus.VERIFIED
            forge_run.approval = ApprovalEngine().evaluate(forge_run.patch, forge_run.verification)
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
