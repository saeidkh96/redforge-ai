from __future__ import annotations

from collections.abc import Iterable

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
        )

    def summarize(self, observations: Iterable[BenchmarkObservation]) -> ReliabilityMetrics:
        items = list(observations)
        passed = sum(item.passed for item in items)
        total = len(items)
        return ReliabilityMetrics(
            total=total,
            passed=passed,
            failed=total - passed,
            success_rate=(passed / total if total else 0.0),
        )
