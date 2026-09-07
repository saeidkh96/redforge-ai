from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from redforge.integrations.git import GitWorkspace
from redforge.integrations.github import GitHubClient
from redforge.models import PullRequest
from redforge.production.models import Permission, RuntimeAction
from redforge.production.runtime import ProductionRuntime


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

    @staticmethod
    def _remote_host(remote_url: str) -> str:
        parsed = urlparse(remote_url)
        if parsed.hostname:
            return parsed.hostname

        # Handle SSH syntax such as git@github.com:owner/repo.git.
        if "@" in remote_url and ":" in remote_url:
            return remote_url.split("@", 1)[1].split(":", 1)[0]

        return remote_url

    def publish(
        self,
        root: str | Path,
        *,
        branch: str,
        commit_message: str,
        title: str,
        body: str,
        create_pr: bool = True,
        remote: str = "origin",
        runtime: ProductionRuntime | None = None,
    ) -> GitHubWorkflowResult:
        workspace = GitWorkspace()

        if runtime is not None:
            runtime.require_allowed(
                RuntimeAction(
                    action="create_branch",
                    permission=Permission.CREATE_BRANCH,
                    resource=str(Path(root).resolve()),
                )
            )

        workspace.create_branch(root, branch)

        status = workspace.status(root)
        commit_created = bool(status.strip())

        if commit_created:
            if runtime is not None:
                runtime.require_allowed(
                    RuntimeAction(
                        action="create_commit",
                        permission=Permission.CREATE_COMMIT,
                        resource=str(Path(root).resolve()),
                    )
                )
            workspace.commit(root, commit_message)

        remote_url = workspace.remote_url(root, remote)
        remote_host = self._remote_host(remote_url)

        if runtime is not None:
            runtime.require_allowed(
                RuntimeAction(
                    action="push_branch",
                    permission=Permission.NETWORK_EGRESS,
                    resource=remote_host,
                )
            )

        workspace.push(root, remote, branch)

        pull_request = None
        if create_pr:
            if runtime is not None:
                runtime.require_allowed(
                    RuntimeAction(
                        action="create_pull_request",
                        permission=Permission.CREATE_PULL_REQUEST,
                        resource=f"{self.owner}/{self.repo}",
                    )
                )
                runtime.require_allowed(
                    RuntimeAction(
                        action="github_api",
                        permission=Permission.NETWORK_EGRESS,
                        resource="api.github.com",
                    )
                )

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
