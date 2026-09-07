from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from redforge.agents import CodingAgent, LLMProvider
from redforge.approval import ApprovalEngine
from redforge.core.config import get_settings
from redforge.execution import PatchEngine, RepairAgent, TestRunner
from redforge.models import (
    Approval,
    ForgeRun,
    Issue,
    RepairAttempt,
    RiskLevel,
    RunStatus,
)
from redforge.persistence import RunStore
from redforge.planning import PlanningEngine
from redforge.production.models import Decision, Permission, RuntimeAction
from redforge.production.review import ReviewCoordinator
from redforge.production.risk import RiskEngine
from redforge.production.runtime import ProductionRuntime
from redforge.repository import RepositoryScanner
from redforge.verification import VerificationEngine
from redforge.verification.advanced import VerificationProfile


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
        use_production_runtime: bool | None = None,
    ) -> ForgeRun:
        if max_repair_attempts < 0:
            raise ValueError("max_repair_attempts must be greater than or equal to zero.")

        settings = get_settings()
        runtime_enabled = (
            settings.e2e_integration_enabled
            if use_production_runtime is None
            else use_production_runtime
        )

        root = Path(repository_path).resolve()
        forge_run = ForgeRun(repository_path=str(root), issue=issue)
        runtime = self._runtime(root) if runtime_enabled else None

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

                if apply_patch and runtime is not None:
                    requires_approval = self._authorize_patch(
                        runtime,
                        root,
                        forge_run,
                        action="apply_patch",
                    )
                    if requires_approval:
                        forge_run.approval = Approval(
                            approved=False,
                            required=True,
                            risk=RiskLevel.HIGH,
                            reasons=[
                                "Runtime policy requires human approval before patch application."
                            ],
                        )
                        forge_run.pending_action = "apply_patch"
                        forge_run.status = RunStatus.AWAITING_APPROVAL
                        forge_run.runtime_evidence = runtime.evidence().model_dump(mode="json")
                        return forge_run

                if apply_patch:
                    PatchEngine().apply(root, forge_run.patch)

            return self._continue_pipeline(
                root,
                forge_run,
                runtime,
                apply_patch=apply_patch,
                repair_on_failure=repair_on_failure,
                max_repair_attempts=max_repair_attempts,
            )

        except Exception as exc:
            forge_run.status = RunStatus.FAILED
            forge_run.error = str(exc)
            return forge_run

        finally:
            forge_run.updated_at = datetime.now(UTC)
            self.store.save(forge_run)

    def resume_after_approval(
        self,
        forge_run: ForgeRun,
        *,
        repair_on_failure: bool = True,
        max_repair_attempts: int = 2,
        use_production_runtime: bool = True,
    ) -> ForgeRun:
        root = Path(forge_run.repository_path).resolve()
        runtime = self._runtime(root) if use_production_runtime else None

        try:
            if forge_run.pending_action != "apply_patch":
                raise RuntimeError("ForgeRun has no resumable patch-application action.")

            if forge_run.approval is None or not forge_run.approval.approved:
                raise PermissionError("Human approval is required before resuming the run.")

            if forge_run.patch is None:
                raise RuntimeError("ForgeRun has no patch to apply.")

            PatchEngine().check(root, forge_run.patch)
            PatchEngine().apply(root, forge_run.patch)

            if runtime is not None:
                runtime.audit.append(
                    event_type="approved_action_executed",
                    actor=forge_run.approval.approver or runtime.principal.id,
                    action="apply_patch",
                    resource=forge_run.id,
                    payload={
                        "files": list(forge_run.patch.files),
                        "approval_actor": forge_run.approval.approver,
                    },
                )

            forge_run.pending_action = None
            forge_run.status = RunStatus.PATCH_READY
            forge_run.error = None

            return self._continue_pipeline(
                root,
                forge_run,
                runtime,
                apply_patch=True,
                repair_on_failure=repair_on_failure,
                max_repair_attempts=max_repair_attempts,
            )

        except Exception as exc:
            forge_run.status = RunStatus.FAILED
            forge_run.error = str(exc)
            return forge_run

        finally:
            forge_run.updated_at = datetime.now(UTC)
            self.store.save(forge_run)

    def _continue_pipeline(
        self,
        root: Path,
        forge_run: ForgeRun,
        runtime: ProductionRuntime | None,
        *,
        apply_patch: bool,
        repair_on_failure: bool,
        max_repair_attempts: int,
    ) -> ForgeRun:
        settings = get_settings()

        current_snapshot = RepositoryScanner().scan(root)
        forge_run.tests = TestRunner().run(root, current_snapshot)
        forge_run.status = RunStatus.TESTED

        self._repair_if_needed(
            root,
            forge_run,
            runtime=runtime,
            apply_patch=apply_patch,
            repair_on_failure=repair_on_failure,
            max_repair_attempts=max_repair_attempts,
        )

        forge_run.status = RunStatus.VERIFYING

        if runtime is not None and settings.advanced_verification_enabled:
            forge_run.verification = runtime.verify_repository(
                VerificationProfile(
                    minimum_coverage=settings.minimum_coverage,
                )
            )

            new_decisions = [
                decision.model_dump(mode="json") for decision in runtime.policy_decisions
            ]
            forge_run.policy_decisions.extend(new_decisions)
        else:
            forge_run.verification = VerificationEngine().verify(root)

        forge_run.status = RunStatus.VERIFIED

        approval = ApprovalEngine().evaluate(
            forge_run.patch,
            forge_run.verification,
        )

        if runtime is not None:
            risk = RiskEngine().evaluate(
                forge_run.patch,
                forge_run.verification,
                runtime.policy_decisions,
            )
            forge_run.risk_assessment = risk.model_dump(mode="json")

            forge_run.status = RunStatus.REVIEWING

            consensus = ReviewCoordinator(
                required_approvals=settings.multi_agent_required_approvals
            ).review(
                forge_run.verification,
                risk,
                runtime.policy_decisions,
            )

            forge_run.review_consensus = consensus.model_dump(mode="json")
            forge_run.status = RunStatus.REVIEWED

            reasons = list(approval.reasons)

            if not consensus.approved:
                reasons.append("Multi-agent verification did not reach approval consensus.")

            if risk.reasons:
                reasons.extend(risk.reasons)

            required = (
                approval.required
                or risk.score >= settings.human_approval_risk_threshold
                or not consensus.approved
            )

            approval = approval.model_copy(
                update={
                    "required": required,
                    "risk": risk.level,
                    "reasons": list(dict.fromkeys(reasons)),
                }
            )

            forge_run.delivery_ready = (
                forge_run.verification.passed and consensus.approved and not required
            )

            runtime.record_run_gate(
                approved=forge_run.delivery_ready,
                risk_score=risk.score,
            )

            evidence = runtime.evidence()
            forge_run.runtime_evidence = evidence.model_copy(
                update={"consensus": consensus}
            ).model_dump(mode="json")

        forge_run.approval = approval

        if forge_run.approval.required:
            forge_run.status = RunStatus.AWAITING_APPROVAL
        elif forge_run.delivery_ready or runtime is None:
            forge_run.status = (
                RunStatus.DELIVERY_READY if runtime is not None else RunStatus.COMPLETED
            )

        return forge_run

    def _authorize_patch(
        self,
        runtime: ProductionRuntime,
        root: Path,
        forge_run: ForgeRun,
        *,
        action: str,
    ) -> bool:
        if forge_run.patch is None:
            return False

        requires_approval = False

        for path in forge_run.patch.files:
            decision = runtime.authorize(
                RuntimeAction(
                    action=action,
                    permission=Permission.WRITE_REPOSITORY,
                    resource=str(root / path),
                )
            )

            if decision.decision == Decision.DENY:
                raise PermissionError(decision.reason)

            if decision.decision == Decision.REQUIRE_APPROVAL:
                requires_approval = True

        forge_run.policy_decisions = [
            decision.model_dump(mode="json") for decision in runtime.policy_decisions
        ]

        return requires_approval

    def _runtime(self, root: Path) -> ProductionRuntime:
        settings = get_settings()

        return ProductionRuntime(
            root,
            allowed_egress_hosts=settings.egress_host_set,
            audit_path=settings.audit_log_path,
        )

    def _repair_if_needed(
        self,
        root: Path,
        forge_run: ForgeRun,
        *,
        apply_patch: bool,
        repair_on_failure: bool,
        max_repair_attempts: int,
        runtime: ProductionRuntime | None = None,
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

            if runtime is not None:
                for path in repair_patch.files:
                    runtime.require_allowed(
                        RuntimeAction(
                            action="apply_repair_patch",
                            permission=Permission.WRITE_REPOSITORY,
                            resource=str(root / path),
                        )
                    )

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
