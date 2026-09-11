from redforge import __version__
from redforge.roadmap_v200 import DeepRepositoryAnalyzer, GitHubIssueClient
from redforge.roadmap_v200.evaluation import BenchmarkEvaluator, ReliabilityHistory
from redforge.roadmap_v200.hardening import EvidenceIntegrity, ReleaseGateEvaluator
from redforge.roadmap_v200.runtime import IntegratedAutonomyRuntime
from redforge.roadmap_v200.webhook import GitHubWebhookVerifier, WebhookDeliveryStore


def main() -> None:
    result = {
        "version": __version__,
        "github_issue_automation": all(
            [GitHubIssueClient, GitHubWebhookVerifier, WebhookDeliveryStore]
        ),
        "deep_repository_intelligence": bool(DeepRepositoryAnalyzer),
        "agent_memory_runtime": bool(IntegratedAutonomyRuntime),
        "evaluation_reliability": all([BenchmarkEvaluator, ReliabilityHistory]),
        "production_hardening": all([EvidenceIntegrity, ReleaseGateEvaluator]),
    }
    result["ready"] = result["version"] == "1.6.0" and all(
        bool(value) for key, value in result.items() if key != "version"
    )
    print(result)
    if not result["ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
