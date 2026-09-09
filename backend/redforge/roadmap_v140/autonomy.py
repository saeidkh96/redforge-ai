import re
from pathlib import Path

from redforge.roadmap_v140.models import GitHubIssueEvent


class GitHubAutonomyPlanner:
    def __init__(self, *, branch_prefix: str = "redforge") -> None:
        self.branch_prefix = branch_prefix

    def branch_for(self, event: GitHubIssueEvent) -> str:
        slug = (
            re.sub(
                r"[^a-z0-9]+",
                "-",
                event.title.lower(),
            ).strip("-")[:48]
            or "issue"
        )
        return f"{self.branch_prefix}/issue-{event.issue_number}-{slug}"

    def issue_prompt(self, event: GitHubIssueEvent) -> str:
        labels = ", ".join(event.labels) if event.labels else "none"
        prompt = (
            f"GitHub issue #{event.issue_number}: {event.title}\n"
            f"Labels: {labels}\n\n"
            f"{event.body.strip()}"
        )
        return prompt.strip()

    def repository_url(self, event: GitHubIssueEvent) -> str:
        return f"https://github.com/{event.owner}/{event.repo}.git"

    def workspace_name(self, event: GitHubIssueEvent) -> str:
        return f"{event.owner}-{event.repo}-{event.issue_number}"

    def workspace_path(
        self,
        root: str | Path,
        event: GitHubIssueEvent,
    ) -> Path:
        return Path(root) / self.workspace_name(event)
