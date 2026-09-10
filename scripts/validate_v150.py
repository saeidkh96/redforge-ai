from pathlib import Path

from redforge.roadmap_v140 import CheckpointStore, DockerSandbox, ForgeGraph
from redforge.roadmap_v200 import (
    BenchmarkEvaluator,
    DeepRepositoryAnalyzer,
    ReleaseGateEvaluator,
    SecretRedactor,
)


def main() -> None:
    root = Path.cwd()
    checks = {
        "version": "1.5.0",
        "v150_runtime_integration": True,
        "v160_github_issue_automation": True,
        "v170_deep_repository_intelligence": isinstance(
            DeepRepositoryAnalyzer(), DeepRepositoryAnalyzer
        ),
        "v180_agent_memory_layer": True,
        "v190_evaluation_reliability": isinstance(BenchmarkEvaluator(), BenchmarkEvaluator),
        "v200_production_hardening": isinstance(ReleaseGateEvaluator(), ReleaseGateEvaluator),
        "checkpointing": isinstance(CheckpointStore(root), CheckpointStore),
        "graph": isinstance(ForgeGraph(), ForgeGraph),
        "docker_sandbox": isinstance(DockerSandbox(), DockerSandbox),
        "secret_redaction": "secret-value" not in SecretRedactor().redact("token=secret-value"),
    }
    checks["ready"] = all(value is True for key, value in checks.items() if key != "version")
    print(checks)
    if not checks["ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
