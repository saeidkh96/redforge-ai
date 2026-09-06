import json
from pathlib import Path

from redforge.production import HashChainAuditLog


def test_hash_chain_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    audit = HashChainAuditLog(path)
    audit.append(
        event_type="test",
        actor="agent",
        action="read",
        resource="repo",
    )
    audit.append(
        event_type="test",
        actor="agent",
        action="verify",
        resource="repo",
    )
    assert audit.verify() is True

    rows = path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(rows[0])
    tampered["action"] = "tampered"
    rows[0] = json.dumps(tampered, sort_keys=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    assert audit.verify() is False
