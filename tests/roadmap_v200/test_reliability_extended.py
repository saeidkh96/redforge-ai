from redforge.roadmap_v200.evaluation import BenchmarkEvaluator
from redforge.roadmap_v200.models import BenchmarkCase


def test_confusion_matrix_metrics() -> None:
    evaluator = BenchmarkEvaluator()
    cases = [
        BenchmarkCase(name="tp", expected_success=True),
        BenchmarkCase(name="tn", expected_success=False),
        BenchmarkCase(name="fp", expected_success=False),
        BenchmarkCase(name="fn", expected_success=True),
    ]
    actual = [True, False, True, False]
    observations = [
        evaluator.observe(case, actual_success=value)
        for case, value in zip(cases, actual, strict=True)
    ]
    metrics = evaluator.summarize(observations)
    assert metrics.true_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_positive == 1
    assert metrics.false_negative == 1
    assert metrics.accuracy == 0.5
