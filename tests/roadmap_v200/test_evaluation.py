from redforge.roadmap_v200 import BenchmarkCase, BenchmarkEvaluator


def test_benchmark_summary() -> None:
    evaluator = BenchmarkEvaluator()
    case = BenchmarkCase(name="known-good", expected_success=True)
    observation = evaluator.observe(case, actual_success=True)
    metrics = evaluator.summarize([observation])
    assert metrics.total == 1
    assert metrics.success_rate == 1.0
