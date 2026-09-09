from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from redforge.roadmap_v140.checkpoint import CheckpointStore
from redforge.roadmap_v140.models import GraphCheckpoint, NodeRecord, NodeStatus

NodeHandler = Callable[[dict[str, Any]], dict[str, Any]]
Condition = Callable[[dict[str, Any]], bool]


@dataclass(slots=True)
class Edge:
    source: str
    target: str
    condition: Condition | None = None


class ForgeGraph:
    def __init__(self, *, checkpoint_store: CheckpointStore | None = None) -> None:
        self._nodes: dict[str, NodeHandler] = {}
        self._edges: list[Edge] = []
        self._entry: str | None = None
        self._checkpoint_store = checkpoint_store

    def add_node(self, name: str, handler: NodeHandler) -> None:
        if not name or name in self._nodes:
            raise ValueError(f"Invalid or duplicate node: {name}")
        self._nodes[name] = handler

    def set_entry(self, name: str) -> None:
        self._require_node(name)
        self._entry = name

    def add_edge(
        self,
        source: str,
        target: str,
        *,
        condition: Condition | None = None,
    ) -> None:
        self._require_node(source)
        self._require_node(target)
        self._edges.append(Edge(source, target, condition))

    def run(
        self,
        checkpoint: GraphCheckpoint,
        *,
        stop_when: Callable[[GraphCheckpoint], bool] | None = None,
        max_steps: int = 100,
    ) -> GraphCheckpoint:
        if not self._entry:
            raise RuntimeError("Graph entry node is not configured.")

        current: str | None = checkpoint.current_node or self._entry
        steps = 0

        while current is not None:
            if steps >= max_steps:
                checkpoint.failed = True
                checkpoint.state["graph_error"] = "Maximum graph steps exceeded."
                self._save(checkpoint)
                return checkpoint

            if stop_when and stop_when(checkpoint):
                checkpoint.current_node = current
                self._save(checkpoint)
                return checkpoint

            record = checkpoint.records.setdefault(
                current,
                NodeRecord(name=current),
            )
            record.status = NodeStatus.RUNNING
            record.attempts += 1
            record.started_at = datetime.now(UTC)
            checkpoint.current_node = current
            self._save(checkpoint)

            try:
                output = self._nodes[current](checkpoint.state)
                checkpoint.state.update(output)
                record.output = output
                record.status = NodeStatus.PASSED
                record.error = None
            except Exception as exc:
                record.status = NodeStatus.FAILED
                record.error = str(exc)
                record.finished_at = datetime.now(UTC)
                checkpoint.failed = True
                self._save(checkpoint)
                return checkpoint

            record.finished_at = datetime.now(UTC)
            current = self._next_node(current, checkpoint.state)
            checkpoint.current_node = current
            steps += 1
            self._save(checkpoint)

        checkpoint.completed = True
        checkpoint.failed = False
        self._save(checkpoint)
        return checkpoint

    def resume(
        self,
        run_id: str,
        *,
        stop_when: Callable[[GraphCheckpoint], bool] | None = None,
        max_steps: int = 100,
    ) -> GraphCheckpoint:
        if self._checkpoint_store is None:
            raise RuntimeError("Checkpoint store is not configured.")

        return self.run(
            self._checkpoint_store.load(run_id),
            stop_when=stop_when,
            max_steps=max_steps,
        )

    def _next_node(
        self,
        source: str,
        state: dict[str, Any],
    ) -> str | None:
        for edge in (item for item in self._edges if item.source == source):
            if edge.condition is None or edge.condition(state):
                return edge.target
        return None

    def _require_node(self, name: str) -> None:
        if name not in self._nodes:
            raise KeyError(f"Unknown node: {name}")

    def _save(self, checkpoint: GraphCheckpoint) -> None:
        checkpoint.updated_at = datetime.now(UTC)
        if self._checkpoint_store is not None:
            self._checkpoint_store.save(checkpoint)
