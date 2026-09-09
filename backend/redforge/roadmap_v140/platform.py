from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

from redforge.roadmap_v140.checkpoint import CheckpointStore
from redforge.roadmap_v140.graph import ForgeGraph
from redforge.roadmap_v140.intelligence import PythonImpactAnalyzer
from redforge.roadmap_v140.memory import EngineeringMemory
from redforge.roadmap_v140.models import AutonomyResult, GraphCheckpoint
from redforge.roadmap_v140.sandbox import DockerSandbox

Stage = Callable[[dict[str, Any]], dict[str, Any]]


class AutonomousEngineeringPlatform:
    DEFAULT_ORDER = (
        "understand",
        "plan",
        "code",
        "patch",
        "test",
        "repair",
        "verify",
        "policy",
        "risk",
        "review",
        "approval",
        "audit",
        "delivery",
    )

    def __init__(
        self, workspace: str | Path, *, stages: dict[str, Stage], use_docker: bool = True
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.stages = stages
        self.checkpoints = CheckpointStore(self.workspace)
        self.memory = EngineeringMemory(
            self.workspace / ".redforge" / "memory" / "engineering.sqlite3"
        )
        self.impact = PythonImpactAnalyzer()
        self.sandbox = DockerSandbox()
        self.use_docker = use_docker

    def build_graph(self) -> ForgeGraph:
        missing = [name for name in self.DEFAULT_ORDER if name not in self.stages]
        if missing:
            raise ValueError("Missing platform stages: " + ", ".join(missing))
        graph = ForgeGraph(checkpoint_store=self.checkpoints)
        for name in self.DEFAULT_ORDER:
            graph.add_node(name, self.stages[name])
        graph.set_entry("understand")
        graph.add_edge("understand", "plan")
        graph.add_edge("plan", "code")
        graph.add_edge("code", "patch")
        graph.add_edge("patch", "test")
        graph.add_edge("test", "repair", condition=lambda s: not bool(s.get("tests_passed", False)))
        graph.add_edge("test", "verify", condition=lambda s: bool(s.get("tests_passed", False)))
        graph.add_edge("repair", "test")
        graph.add_edge("verify", "policy")
        graph.add_edge("policy", "risk")
        graph.add_edge("risk", "review")
        graph.add_edge("review", "approval")
        graph.add_edge("approval", "audit")
        graph.add_edge("audit", "delivery")
        return graph

    def start(self, initial_state: dict[str, Any], *, run_id: str | None = None) -> AutonomyResult:
        checkpoint = GraphCheckpoint(run_id=run_id or str(uuid4()), state=dict(initial_state))
        completed = self.build_graph().run(
            checkpoint,
            stop_when=lambda item: bool(item.state.get("awaiting_human_approval", False)),
            max_steps=100,
        )
        return self._result(completed)

    def resume(self, run_id: str, *, approval_granted: bool) -> AutonomyResult:
        checkpoint = self.checkpoints.load(run_id)
        checkpoint.state["human_approval_granted"] = approval_granted
        checkpoint.state["awaiting_human_approval"] = False
        completed = self.build_graph().run(checkpoint, max_steps=100)
        return self._result(completed)

    def _result(self, checkpoint: GraphCheckpoint) -> AutonomyResult:
        return AutonomyResult(
            run_id=checkpoint.run_id,
            checkpoint=checkpoint,
            delivery_ready=bool(checkpoint.state.get("delivery_ready", False)),
            branch=checkpoint.state.get("branch"),
            pull_request_url=checkpoint.state.get("pull_request_url"),
            evidence={
                "docker_enabled": self.use_docker,
                "checkpointed": True,
                "memory_path": str(self.memory.path),
            },
        )
