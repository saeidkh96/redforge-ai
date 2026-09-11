from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from pathlib import Path
from typing import Any

from redforge.roadmap_v200.models import GitHubIssueSpec, GitHubWebhookEvent


class GitHubWebhookVerifier:
    def __init__(self, secret: str) -> None:
        self.secret = secret.encode("utf-8")

    def verify(self, body: bytes, signature: str | None) -> bool:
        if not signature or not signature.startswith("sha256="):
            return False
        expected = "sha256=" + hmac.new(self.secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class WebhookDeliveryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS github_deliveries ("
                "delivery_id TEXT PRIMARY KEY, processed_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def claim(self, delivery_id: str) -> bool:
        try:
            with sqlite3.connect(self.path) as db:
                db.execute("INSERT INTO github_deliveries(delivery_id) VALUES (?)", (delivery_id,))
            return True
        except sqlite3.IntegrityError:
            return False


class GitHubWebhookParser:
    ALLOWED_ACTIONS = {"opened", "reopened", "labeled"}

    def parse(self, body: bytes, delivery_id: str) -> GitHubWebhookEvent:
        raw: Any = json.loads(body.decode("utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("GitHub webhook payload must be an object.")
        action = str(raw.get("action", ""))
        if action not in self.ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported GitHub issue action: {action}")
        issue = raw.get("issue")
        repository = raw.get("repository")
        sender = raw.get("sender")
        if not isinstance(issue, dict) or not isinstance(repository, dict):
            raise ValueError("Webhook payload is missing issue/repository data.")
        owner_data = repository.get("owner")
        owner = owner_data.get("login") if isinstance(owner_data, dict) else None
        repo = repository.get("name")
        labels_raw = issue.get("labels") or []
        labels = [
            str(item.get("name"))
            for item in labels_raw
            if isinstance(item, dict) and item.get("name")
        ]
        return GitHubWebhookEvent(
            delivery_id=delivery_id,
            action=action,
            issue=GitHubIssueSpec(
                owner=str(owner or ""),
                repo=str(repo or ""),
                issue_number=int(issue.get("number", 0)),
                title=str(issue.get("title", "")),
                body=str(issue.get("body") or ""),
                labels=labels,
                html_url=str(issue.get("html_url") or "") or None,
                sender=str((sender or {}).get("login") or "") if isinstance(sender, dict) else None,
            ),
        )
