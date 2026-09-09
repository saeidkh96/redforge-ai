from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from redforge.roadmap_v140.models import MemoryRecord


class EngineeringMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def put(
        self,
        key: str,
        value: dict[str, Any],
        *,
        namespace: str = "default",
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        now = datetime.now(UTC)

        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO memory (
                    namespace,
                    key,
                    value_json,
                    tags_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    value_json = excluded.value_json,
                    tags_json = excluded.tags_json,
                    updated_at = excluded.updated_at
                """,
                (
                    namespace,
                    key,
                    json.dumps(value, sort_keys=True),
                    json.dumps(tags or []),
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            connection.commit()

        return self.get(
            key,
            namespace=namespace,
        )

    def get(
        self,
        key: str,
        *,
        namespace: str = "default",
    ) -> MemoryRecord:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT
                    value_json,
                    tags_json,
                    created_at,
                    updated_at
                FROM memory
                WHERE namespace = ? AND key = ?
                """,
                (
                    namespace,
                    key,
                ),
            ).fetchone()

        if row is None:
            raise KeyError(f"Memory record not found: {namespace}/{key}")

        return MemoryRecord(
            key=key,
            namespace=namespace,
            value=json.loads(row[0]),
            tags=json.loads(row[1]),
            created_at=datetime.fromisoformat(row[2]),
            updated_at=datetime.fromisoformat(row[3]),
        )

    def search(
        self,
        text: str,
        *,
        namespace: str | None = None,
    ) -> list[MemoryRecord]:
        query = "%" + text.lower() + "%"

        sql = """
            SELECT
                namespace,
                key,
                value_json,
                tags_json,
                created_at,
                updated_at
            FROM memory
            WHERE (
                lower(key) LIKE ?
                OR lower(value_json) LIKE ?
                OR lower(tags_json) LIKE ?
            )
        """

        params: list[Any] = [
            query,
            query,
            query,
        ]

        if namespace is not None:
            sql += " AND namespace = ?"
            params.append(namespace)

        sql += " ORDER BY updated_at DESC"

        with self._connection() as connection:
            rows = connection.execute(
                sql,
                params,
            ).fetchall()

        return [
            MemoryRecord(
                namespace=row[0],
                key=row[1],
                value=json.loads(row[2]),
                tags=json.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5]),
            )
            for row in rows
        ]

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(namespace, key)
                )
                """
            )
            connection.commit()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.path,
            timeout=5.0,
        )

        try:
            yield connection
        finally:
            connection.close()
