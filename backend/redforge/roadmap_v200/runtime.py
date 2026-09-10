from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from redforge.agents import LLMProvider
from redforge.core.orchestrator import ForgeOrchestrator
from redforge.models import ForgeRun, Issue, RunStatus
from redforge.roadmap_v140 import CheckpointStore, DockerSandbox, ForgeGraph, GraphCheckpoint
from redforge.roadmap_v140.memory import EngineeringMemory
from redforge.roadmap_v200.hardening import ReleaseGateEvaluator
from redforge.roadmap_v200.intelligence import DeepRepositoryAnalyzer
from redforge.roadmap_v200.models import AutonomousRunReport, DeepImpactReport, ReleaseGate


class IntegratedAutonomyRuntime:
    """Graph-orchestrated adapter around the established production ForgeRun pipeline."""

    def __init__(
        self,
        workspace: str | Path,
        *,
        provider: LLMProvider | None = None,
        docker_probe: bool = True,
        execute_docker_probe: bool = False,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.provider = provider
        self.docker_probe = docker_probe
        self.execute_docker_probe = execute_docker_probe
        self.checkpoints = CheckpointStore(self.workspace)
        self.memory = EngineeringMemory(
            self.workspace / ".redforge" / "memory" / "engineering.sqlite3"
        )
        self.intelligence = DeepRepositoryAnalyzer()
        self.gates = ReleaseGateEvaluator()
        self.sandbox = DockerSandbox()

    def run_issue(
        self,
        issue: Issue,
        *,
        generate_patch: bool = False,
        apply_patch: bool = False,
        repair_on_failure: bool = True,
        max_repair_attempts: int = 2,
        run_id: str | None = None,
    ) -> AutonomousRunReport:
        checkpoint = GraphCheckpoint(
            run_id=run_id or str(uuid4()),
            state={
                "issue": issue.model_dump(mode="json"),
                "generate_patch": generate_patch,
                "apply_patch": apply_patch,
                "repair_on_failure": repair_on_failure,
                "max_repair_attempts": max_repair_attempts,
            },
        )
        completed = self._graph().run(checkpoint, max_steps=10)
        return self._report(completed)

    def resume(self, run_id: str) -> AutonomousRunReport:
        completed = self._graph().resume(run_id, max_steps=10)
        return self._report(completed)

    def _graph(self) -> ForgeGraph:
        graph = ForgeGraph(checkpoint_store=self.checkpoints)
        graph.add_node("intelligence", self._intelligence_stage)
        graph.add_node("forge", self._forge_stage)
        graph.add_node("sandbox", self._sandbox_stage)
        graph.add_node("gate", self._gate_stage)
        graph.add_node("memory", self._memory_stage)
        graph.set_entry("intelligence")
        graph.add_edge("intelligence", "forge")
        graph.add_edge("forge", "sandbox")
        graph.add_edge("sandbox", "gate")
        graph.add_edge("gate", "memory")
        return graph

    def _intelligence_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        report = self.intelligence.analyze(self.workspace, [])
        return {"preflight_impact": report.model_dump(mode="json")}

    def _forge_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        issue = Issue.model_validate(state["issue"])
        run = ForgeOrchestrator(provider=self.provider).run(
            self.workspace,
            issue,
            generate_patch=bool(state.get("generate_patch", False)),
            apply_patch=bool(state.get("apply_patch", False)),
            repair_on_failure=bool(state.get("repair_on_failure", True)),
            max_repair_attempts=int(state.get("max_repair_attempts", 2)),
            use_production_runtime=True,
        )
        changed_files = list(run.patch.files) if run.patch is not None else []
        impact = self.intelligence.analyze(self.workspace, changed_files)
        return {
            "forge_run": run.model_dump(mode="json"),
            "impact": impact.model_dump(mode="json"),
            "awaiting_human_approval": run.status == RunStatus.AWAITING_APPROVAL,
        }

    def _sandbox_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        if not self.docker_probe:
            return {"docker_evidence": {"enabled": False}}
        result = self.sandbox.run(
            self.workspace,
            ["python", "--version"],
            dry_run=not self.execute_docker_probe,
        )
        return {
            "docker_evidence": {
                "enabled": True,
                "executed": self.execute_docker_probe,
                "available": self.sandbox.available(),
                "result": result.model_dump(mode="json"),
            }
        }

    def _gate_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        run = ForgeRun.model_validate(state["forge_run"])
        evidence = self._gate_evidence(run)
        gate = self.gates.evaluate(evidence)
        return {"release_gate": gate.model_dump(mode="json"), "gate_evidence": evidence}

    def _memory_stage(self, state: dict[str, Any]) -> dict[str, Any]:
        run = ForgeRun.model_validate(state["forge_run"])
        impact = DeepImpactReport.model_validate(state["impact"])
        gate = ReleaseGate.model_validate(state["release_gate"])
        self.memory.put(
            key=f"forge-run:{run.id}",
            value={
                "status": run.status.value,
                "delivery_ready": run.delivery_ready,
                "impact_score": impact.risk_score,
                "release_gate_passed": gate.passed,
            },
            namespace="v2-runs",
            tags=["forge-run", "autonomy", run.status.value],
        )
        return {"memory_recorded": True}

    def _report(self, checkpoint: GraphCheckpoint) -> AutonomousRunReport:
        state = checkpoint.state
        run_data = state.get("forge_run")
        run = ForgeRun.model_validate(run_data) if run_data else None
        impact_data = state.get("impact")
        impact = DeepImpactReport.model_validate(impact_data) if impact_data else None
        gate_data = state.get("release_gate")
        gate = ReleaseGate.model_validate(gate_data) if gate_data else None
        delivery_ready = bool(run and run.delivery_ready and gate and gate.passed)
        return AutonomousRunReport(
            run_id=run.id if run else checkpoint.run_id,
            status=run.status.value if run else ("failed" if checkpoint.failed else "running"),
            delivery_ready=delivery_ready,
            pull_request_url=(run.pull_request.url if run and run.pull_request else None),
            impact=impact,
            gate=gate,
            evidence={
                "checkpoint_run_id": checkpoint.run_id,
                "checkpoint_completed": checkpoint.completed,
                "checkpoint_failed": checkpoint.failed,
                "docker": state.get("docker_evidence", {}),
                "gate_evidence": state.get("gate_evidence", {}),
                "forge_run": run.model_dump(mode="json") if run else None,
            },
        )

    @staticmethod
    def _gate_evidence(run: ForgeRun) -> dict[str, Any]:
        verification_passed = bool(run.verification and run.verification.passed)
        review_approved = bool(run.review_consensus and run.review_consensus.get("approved"))
        runtime = run.runtime_evidence or {}
        approval_required = bool(run.approval and run.approval.required)
        approval_granted = bool(run.approval and run.approval.approved)
        return {
            "verification_passed": verification_passed,
            "review_approved": review_approved,
            "audit_present": bool(runtime),
            "human_approval_required": approval_required,
            "human_approval_granted": approval_granted,
        }
