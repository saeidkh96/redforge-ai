from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from redforge.production.models import AuditEvent


class HashChainAuditLog:
    GENESIS_HASH = "0" * 64

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> bytes:
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")

    def _read_raw(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def append(
        self,
        *,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEvent:
        rows = self._read_raw()
        previous_hash = rows[-1]["event_hash"] if rows else self.GENESIS_HASH
        sequence = len(rows) + 1
        timestamp = datetime.now(UTC)

        body = {
            "sequence": sequence,
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "resource": resource,
            "payload": payload or {},
            "previous_hash": previous_hash,
        }
        event_hash = hashlib.sha256(
            previous_hash.encode("ascii") + self._canonical(body)
        ).hexdigest()
        body["event_hash"] = event_hash

        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(body, sort_keys=True) + "\n")

        return AuditEvent.model_validate(body)

    def verify(self) -> bool:
        rows = self._read_raw()
        previous_hash = self.GENESIS_HASH

        for expected_sequence, row in enumerate(rows, start=1):
            if row.get("sequence") != expected_sequence:
                return False
            if row.get("previous_hash") != previous_hash:
                return False

            candidate = dict(row)
            observed_hash = candidate.pop("event_hash", "")
            expected_hash = hashlib.sha256(
                previous_hash.encode("ascii") + self._canonical(candidate)
            ).hexdigest()
            if observed_hash != expected_hash:
                return False

            previous_hash = observed_hash

        return True
