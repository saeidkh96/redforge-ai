from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, cast
from urllib import error, request

from redforge.agents import LLMProvider
from redforge.core.config import get_settings
from redforge.models import ForgeRun, Issue
from redforge.production.github_workflow import GitHubWorkflow
from redforge.production.runtime import ProductionRuntime
from redforge.roadmap_v140.autonomy import GitHubAutonomyPlanner
from redforge.roadmap_v140.models import GitHubIssueEvent
from redforge.roadmap_v200.models import AutonomousRunReport, GitHubIssueSpec
from redforge.roadmap_v200.runtime import IntegratedAutonomyRuntime


class GitHubIssueClient:
    def __init__(self, token: str, *, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def fetch_issue(self, owner: str, repo: str, issue_number: int) -> GitHubIssueSpec:
        data = self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
        raw_labels = data.get("labels", [])
        labels: list[str] = []
        if isinstance(raw_labels, list):
            for item in raw_labels:
                if isinstance(item, dict):
                    name = item.get("name")
                    if isinstance(name, str):
                        labels.append(name)
        title = data.get("title", "")
        body = data.get("body", "")
        return GitHubIssueSpec(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            title=title if isinstance(title, str) else str(title),
            body=body if isinstance(body, str) else "",
            labels=labels,
        )

    def comment(self, issue: GitHubIssueSpec, body: str) -> str | None:
        data = self._request(
            "POST",
            f"/repos/{issue.owner}/{issue.repo}/issues/{issue.issue_number}/comments",
            {"body": body},
        )
        value = data.get("html_url")
        return value if isinstance(value, str) else None

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"https://api.github.com{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "redforge-ai",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw: Any = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API failed with HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc
        if not isinstance(raw, dict):
            raise RuntimeError("GitHub API returned an unexpected response.")
        return cast(dict[str, object], raw)


class GitHubAutonomyRunner:
    """Issue -> workspace -> ForgeRun -> optional audited branch/commit/push/PR."""

    def __init__(
        self,
        *,
        token: str,
        workspace_root: str | Path,
        provider: LLMProvider | None = None,
    ) -> None:
        self.token = token
        self.workspace_root = Path(workspace_root).resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.provider = provider
        self.client = GitHubIssueClient(token)

    def run(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        *,
        generate_patch: bool = True,
        apply_patch: bool = True,
        publish: bool = False,
        actor: str = "redforge-agent",
    ) -> AutonomousRunReport:
        issue_spec = self.client.fetch_issue(owner, repo, issue_number)
        event = GitHubIssueEvent(**issue_spec.model_dump())
        planner = GitHubAutonomyPlanner()
        workspace = self.workspace_root / planner.workspace_name(event)
        self._ensure_repository(workspace, planner.repository_url(event))

        report = IntegratedAutonomyRuntime(workspace, provider=self.provider).run_issue(
            Issue(title=issue_spec.title, body=issue_spec.body, labels=issue_spec.labels),
            generate_patch=generate_patch,
            apply_patch=apply_patch,
        )
        branch = planner.branch_for(event)
        report.branch = branch

        if not publish:
            return report
        if not apply_patch:
            raise RuntimeError("Publishing requires apply_patch=True.")
        if not report.delivery_ready:
            raise RuntimeError("Run is not delivery-ready; refusing GitHub publication.")

        run_data = report.evidence.get("forge_run")
        if not isinstance(run_data, dict):
            raise RuntimeError("ForgeRun evidence is missing.")
        forge_run = ForgeRun.model_validate(run_data)
        settings = get_settings()
        runtime = ProductionRuntime(
            workspace,
            actor=actor,
            allowed_egress_hosts=settings.egress_host_set,
            audit_path=settings.audit_log_path,
        )
        result = GitHubWorkflow(owner=owner, repo=repo, token=self.token).publish(
            workspace,
            branch=branch,
            commit_message=f"feat: resolve issue #{issue_number} with RedForge",
            title=issue_spec.title,
            body=f"Automated RedForge change for issue #{issue_number}.",
            create_pr=True,
            runtime=runtime,
        )
        forge_run.pull_request = result.pull_request
        forge_run.delivery_ready = True
        report.pull_request_url = result.pull_request.url if result.pull_request else None
        report.evidence["github_delivery"] = {
            "branch": result.branch,
            "commit_created": result.commit_created,
            "pull_request_url": report.pull_request_url,
        }
        return report

    @staticmethod
    def _ensure_repository(workspace: Path, repository_url: str) -> None:
        if (workspace / ".git").exists():
            return
        if workspace.exists() and any(workspace.iterdir()):
            raise RuntimeError(f"Workspace exists and is not a Git repository: {workspace}")
        workspace.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repository_url, str(workspace)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git clone failed")
