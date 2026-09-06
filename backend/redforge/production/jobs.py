from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from uuid import uuid4


class JobManager[T]:
    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: dict[str, Future[T]] = {}
        self._lock = Lock()

    def submit(
        self,
        fn: Callable[..., T],
        *args: object,
        **kwargs: object,
    ) -> str:
        job_id = str(uuid4())
        future = self._executor.submit(fn, *args, **kwargs)

        with self._lock:
            self._jobs[job_id] = future

        return job_id

    def status(self, job_id: str) -> str:
        with self._lock:
            future = self._jobs[job_id]

        if future.cancelled():
            return "cancelled"

        if future.done():
            return "failed" if future.exception() else "completed"

        if future.running():
            return "running"

        return "queued"

    def result(self, job_id: str) -> T:
        with self._lock:
            future = self._jobs[job_id]

        return future.result()
