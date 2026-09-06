from __future__ import annotations

from collections import defaultdict

from redforge.production.models import ReviewerOutcome, ReviewerScore


class ReviewerReliabilityTracker:
    def score(self, outcomes: list[ReviewerOutcome]) -> list[ReviewerScore]:
        grouped: dict[str, list[ReviewerOutcome]] = defaultdict(list)
        for outcome in outcomes:
            grouped[outcome.reviewer].append(outcome)

        scores: list[ReviewerScore] = []
        for reviewer, rows in sorted(grouped.items()):
            tp = sum(r.expected_safe and r.predicted_safe for r in rows)
            tn = sum((not r.expected_safe) and (not r.predicted_safe) for r in rows)
            fp = sum((not r.expected_safe) and r.predicted_safe for r in rows)
            fn = sum(r.expected_safe and (not r.predicted_safe) for r in rows)
            total = len(rows)

            precision = tp / (tp + fp) if tp + fp else 1.0
            recall = tp / (tp + fn) if tp + fn else 1.0
            accuracy = (tp + tn) / total if total else 0.0

            # Conservative reliability: harmonic mean of precision, recall and accuracy.
            values = [precision, recall, accuracy]
            reliability = (
                len(values) / sum(1 / max(value, 1e-9) for value in values) if values else 0.0
            )
            scores.append(
                ReviewerScore(
                    reviewer=reviewer,
                    true_positive=tp,
                    true_negative=tn,
                    false_positive=fp,
                    false_negative=fn,
                    precision=precision,
                    recall=recall,
                    accuracy=accuracy,
                    reliability=reliability,
                )
            )
        return scores
