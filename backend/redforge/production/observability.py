from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock
from time import perf_counter


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._durations: dict[str, float] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    @contextmanager
    def timer(self, name: str) -> Iterator[None]:
        started = perf_counter()
        try:
            yield
        finally:
            elapsed = perf_counter() - started
            with self._lock:
                self._durations[name] = self._durations.get(name, 0.0) + elapsed

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            data: dict[str, float] = {key: float(value) for key, value in self._counters.items()}

            data.update({f"{key}_seconds": value for key, value in self._durations.items()})

            return data
