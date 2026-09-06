from __future__ import annotations

import json
from urllib import error, request

from redforge.models import PullRequest


class GitHubClient:
    def __init__(self, token: str, api_base: str = "https://api.github.com") -> None:
        self.token = token
        self.api_base = api_base.rstrip("/")

    def create_pull_request(self, owner: str, repo: str, pull_request: PullRequest) -> PullRequest:
        payload = json.dumps(
            {
                "title": pull_request.title,
                "body": pull_request.body,
                "head": pull_request.head,
                "base": pull_request.base,
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.api_base}/repos/{owner}/{repo}/pulls",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API error {exc.code}: {detail}") from exc
        return pull_request.model_copy(
            update={"number": data.get("number"), "url": data.get("html_url")}
        )
