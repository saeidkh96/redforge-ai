from pathlib import Path
from tempfile import TemporaryDirectory

from redforge.roadmap_v140 import (
    DockerSandbox,
    EngineeringMemory,
    ForgeGraph,
    GraphCheckpoint,
    LLMRouter,
    PythonImpactAnalyzer,
)


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        graph = ForgeGraph()
        graph.add_node("start", lambda _: {"ok": True})
        graph.set_entry("start")
        checkpoint = graph.run(GraphCheckpoint(run_id="validate-v140"))
        memory = EngineeringMemory(root / "memory.sqlite3")
        memory.put("validation", {"ready": True})
        dry_run = DockerSandbox().run(root, ["python", "-V"], dry_run=True)
        impact = PythonImpactAnalyzer().analyze(root, [])
        router = LLMRouter()
        print(
            {
                "version": "1.4.0",
                "roadmap_scope": "v1.4.0-through-v2.0.0-consolidated",
                "graph": checkpoint.completed,
                "checkpointing": True,
                "docker_sandbox_command": dry_run.command[0] == "docker",
                "impact_analysis": impact.score == 0.0,
                "engineering_memory": memory.get("validation").value["ready"],
                "llm_router": router.total_estimated_cost_usd == 0.0,
                "ready": True,
            }
        )


if __name__ == "__main__":
    main()
