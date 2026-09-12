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
    """Persistent webhook idempotency with retry-safe delivery states."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS github_deliveries ("
                "delivery_id TEXT PRIMARY KEY, "
                "status TEXT NOT NULL DEFAULT 'completed', "
                "updated_at TEXT DEFAULT CURRENT_TIMESTAMP, "
                "error TEXT)"
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(github_deliveries)")}
            if "status" not in columns:
                db.execute(
                    "ALTER TABLE github_deliveries "
                    "ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'"
                )
            if "updated_at" not in columns:
                db.execute("ALTER TABLE github_deliveries ADD COLUMN updated_at TEXT")
            if "error" not in columns:
                db.execute("ALTER TABLE github_deliveries ADD COLUMN error TEXT")

    def begin(self, delivery_id: str) -> bool:
        """Claim a new or previously failed delivery.

        Completed or currently processing deliveries are treated as duplicates.
        Failed deliveries may be retried safely.
        """
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT status FROM github_deliveries WHERE delivery_id = ?",
                (delivery_id,),
            ).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO github_deliveries(delivery_id, status, updated_at, error) "
                    "VALUES (?, 'processing', CURRENT_TIMESTAMP, NULL)",
                    (delivery_id,),
                )
                return True
            if row[0] == "failed":
                db.execute(
                    "UPDATE github_deliveries SET status = 'processing', "
                    "updated_at = CURRENT_TIMESTAMP, error = NULL WHERE delivery_id = ?",
                    (delivery_id,),
                )
                return True
            return False

    def complete(self, delivery_id: str) -> None:
        self._set_state(delivery_id, "completed", None)

    def fail(self, delivery_id: str, error: str) -> None:
        self._set_state(delivery_id, "failed", error[:2000])

    def status(self, delivery_id: str) -> str | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT status FROM github_deliveries WHERE delivery_id = ?",
                (delivery_id,),
            ).fetchone()
        return str(row[0]) if row else None

    def claim(self, delivery_id: str) -> bool:
        """Backward-compatible one-step claim used by older callers/tests."""
        if not self.begin(delivery_id):
            return False
        self.complete(delivery_id)
        return True

    def _set_state(self, delivery_id: str, status: str, error: str | None) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE github_deliveries SET status = ?, updated_at = CURRENT_TIMESTAMP, "
                "error = ? WHERE delivery_id = ?",
                (status, error, delivery_id),
            )


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
        issue_number = int(issue.get("number", 0))
        if not owner or not repo or issue_number < 1:
            raise ValueError("Webhook payload contains invalid repository or issue identity.")
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
                owner=str(owner),
                repo=str(repo),
                issue_number=issue_number,
                title=str(issue.get("title", "")),
                body=str(issue.get("body") or ""),
                labels=labels,
                html_url=str(issue.get("html_url") or "") or None,
                sender=str((sender or {}).get("login") or "") if isinstance(sender, dict) else None,
            ),
        )
