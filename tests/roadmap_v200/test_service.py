from pathlib import Path

from redforge.roadmap_v200 import AutonomousEngineeringService, GitHubIssueSpec


def test_github_envelope(tmp_path: Path) -> None:
    service = AutonomousEngineeringService(tmp_path)
    result = service.github_envelope(
        GitHubIssueSpec(owner="acme", repo="demo", issue_number=12, title="Fix parser")
    )
    assert result["branch"].startswith("redforge/issue-12-")
    assert result["repository_url"] == "https://github.com/acme/demo.git"
