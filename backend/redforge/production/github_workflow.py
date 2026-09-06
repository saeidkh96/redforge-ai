from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from redforge.integrations.git import GitWorkspace
from redforge.integrations.github import GitHubClient
from redforge.models import PullRequest


@dataclass(slots=True)
class GitHubWorkflowResult:
    branch: str
    commit_created: bool
    pull_request: PullRequest | None


class GitHubWorkflow:
    def __init__(
        self,
        *,
        owner: str,
        repo: str,
        token: str,
        base_branch: str = "main",
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_branch = base_branch

    def publish(
        self,
        root: str | Path,
        *,
        branch: str,
        commit_message: str,
        title: str,
        body: str,
        create_pr: bool = True,
    ) -> GitHubWorkflowResult:
        workspace = GitWorkspace()

        workspace.create_branch(root, branch)

        status = workspace.status(root)
        commit_created = bool(status.strip())

        if commit_created:
            workspace.commit(root, commit_message)

        pull_request = None

        if create_pr:
            client = GitHubClient(self.token)

            pull_request = PullRequest(
                title=title,
                body=body,
                head=branch,
                base=self.base_branch,
            )

            pull_request = client.create_pull_request(
                self.owner,
                self.repo,
                pull_request,
            )

        return GitHubWorkflowResult(
            branch=branch,
            commit_created=commit_created,
            pull_request=pull_request,
        )
