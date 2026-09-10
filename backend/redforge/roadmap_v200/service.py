from __future__ import annotations

from pathlib import Path

from redforge.agents import LLMProvider
from redforge.roadmap_v140.autonomy import GitHubAutonomyPlanner
from redforge.roadmap_v140.models import GitHubIssueEvent
from redforge.roadmap_v200.github_live import GitHubAutonomyRunner
from redforge.roadmap_v200.models import AutonomousRunReport, GitHubIssueSpec
from redforge.roadmap_v200.runtime import IntegratedAutonomyRuntime


class AutonomousEngineeringService:
    def __init__(self, workspace: str | Path, *, provider: LLMProvider | None = None) -> None:
        self.workspace = Path(workspace).resolve()
        self.provider = provider

    def run_local_issue(
        self,
        title: str,
        body: str = "",
        *,
        labels: list[str] | None = None,
        generate_patch: bool = False,
        apply_patch: bool = False,
    ) -> AutonomousRunReport:
        from redforge.models import Issue

        return IntegratedAutonomyRuntime(self.workspace, provider=self.provider).run_issue(
            Issue(title=title, body=body, labels=labels or []),
            generate_patch=generate_patch,
            apply_patch=apply_patch,
        )

    def github_envelope(self, issue: GitHubIssueSpec) -> dict[str, str]:
        event = GitHubIssueEvent(
            owner=issue.owner,
            repo=issue.repo,
            issue_number=issue.issue_number,
            title=issue.title,
            body=issue.body,
            labels=issue.labels,
        )
        planner = GitHubAutonomyPlanner()
        return {
            "repository_url": planner.repository_url(event),
            "branch": planner.branch_for(event),
            "prompt": planner.issue_prompt(event),
            "workspace_name": planner.workspace_name(event),
        }

    def github_runner(self, token: str) -> GitHubAutonomyRunner:
        return GitHubAutonomyRunner(
            token=token,
            workspace_root=self.workspace,
            provider=self.provider,
        )
