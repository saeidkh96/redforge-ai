from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from redforge.roadmap_v200.models import BenchmarkCase, BenchmarkObservation, ReliabilityMetrics


class BenchmarkEvaluator:
    def observe(
        self,
        case: BenchmarkCase,
        *,
        actual_success: bool,
        actual_delivery_ready: bool | None = None,
    ) -> BenchmarkObservation:
        passed = actual_success == case.expected_success
        if case.expected_delivery_ready is not None:
            passed = passed and actual_delivery_ready == case.expected_delivery_ready
        return BenchmarkObservation(
            name=case.name,
            expected_success=case.expected_success,
            actual_success=actual_success,
            expected_delivery_ready=case.expected_delivery_ready,
            actual_delivery_ready=actual_delivery_ready,
            passed=passed,
            category=case.category,
        )

    def summarize(self, observations: Iterable[BenchmarkObservation]) -> ReliabilityMetrics:
        items = list(observations)
        passed = sum(item.passed for item in items)
        total = len(items)
        tp = sum(item.expected_success and item.actual_success for item in items)
        tn = sum((not item.expected_success) and (not item.actual_success) for item in items)
        fp = sum((not item.expected_success) and item.actual_success for item in items)
        fn = sum(item.expected_success and (not item.actual_success) for item in items)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        accuracy = passed / total if total else 1.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return ReliabilityMetrics(
            total=total,
            passed=passed,
            failed=total - passed,
            success_rate=accuracy,
            true_positive=tp,
            true_negative=tn,
            false_positive=fp,
            false_negative=fn,
            precision=precision,
            recall=recall,
            accuracy=accuracy,
            f1=f1,
        )


class ReliabilityHistory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, metrics: ReliabilityMetrics) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics.model_dump(mode="json"), sort_keys=True) + "\n")

    def latest(self) -> ReliabilityMetrics | None:
        if not self.path.exists():
            return None
        lines = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line]
        return ReliabilityMetrics.model_validate_json(lines[-1]) if lines else None
