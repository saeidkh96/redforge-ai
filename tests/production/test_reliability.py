from redforge.production import ReviewerOutcome, ReviewerReliabilityTracker


def test_reviewer_reliability_tracks_false_results() -> None:
    tracker = ReviewerReliabilityTracker()
    scores = tracker.score(
        [
            ReviewerOutcome(
                reviewer="reviewer-a",
                expected_safe=True,
                predicted_safe=True,
            ),
            ReviewerOutcome(
                reviewer="reviewer-a",
                expected_safe=False,
                predicted_safe=True,
            ),
        ]
    )
    assert len(scores) == 1
    assert scores[0].false_positive == 1
    assert 0.0 <= scores[0].reliability <= 1.0
