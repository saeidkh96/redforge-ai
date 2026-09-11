import hashlib
import hmac
import json
from pathlib import Path

from redforge.roadmap_v200.webhook import (
    GitHubWebhookParser,
    GitHubWebhookVerifier,
    WebhookDeliveryStore,
)


def test_webhook_verification_and_parse() -> None:
    body = json.dumps(
        {
            "action": "opened",
            "issue": {
                "number": 7,
                "title": "Fix bug",
                "body": "Please fix it",
                "labels": [{"name": "redforge"}],
                "html_url": "https://github.com/o/r/issues/7",
            },
            "repository": {"name": "r", "owner": {"login": "o"}},
            "sender": {"login": "saeid"},
        }
    ).encode()
    secret = "secret"
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert GitHubWebhookVerifier(secret).verify(body, signature)
    event = GitHubWebhookParser().parse(body, "delivery-1")
    assert event.issue.owner == "o"
    assert event.issue.issue_number == 7
    assert event.issue.labels == ["redforge"]


def test_delivery_store_is_idempotent(tmp_path: Path) -> None:
    store = WebhookDeliveryStore(tmp_path / "deliveries.sqlite3")
    assert store.claim("abc") is True
    assert store.claim("abc") is False
