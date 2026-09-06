from redforge.models import Issue, Plan, PlanStep
from redforge.repository import RepositorySnapshot


class PlanningEngine:
    def create_plan(self, issue: Issue, snapshot: RepositorySnapshot) -> Plan:
        title = issue.title.strip() or "Untitled issue"
        likely_targets = self._select_targets(issue, snapshot)
        steps = [
            PlanStep(
                order=1,
                title="Understand affected code",
                description=(
                    "Review repository context, relevant symbols, dependencies, "
                    "tests, and entry points."
                ),
                target_files=likely_targets,
                verification=["Repository snapshot remains reproducible"],
            ),
            PlanStep(
                order=2,
                title="Implement minimal patch",
                description=(f"Implement the smallest safe change that addresses: {title}"),
                target_files=likely_targets,
                verification=[
                    "Patch applies cleanly",
                    "No unrelated files are modified",
                ],
            ),
            PlanStep(
                order=3,
                title="Validate change",
                description=("Run repository-native tests and deterministic verification checks."),
                target_files=snapshot.test_files[:10],
                verification=[
                    "Tests pass",
                    "Security scan has no blocking findings",
                ],
            ),
        ]
        risks: list[str] = []
        if snapshot.git and snapshot.git.is_dirty:
            risks.append("Repository already contains uncommitted changes.")
        if not snapshot.test_files:
            risks.append("No test files were detected.")
        if not likely_targets:
            risks.append("No likely target files could be inferred from the issue text.")
        return Plan(summary=f"Plan for: {title}", steps=steps, risks=risks)

    @staticmethod
    def _select_targets(issue: Issue, snapshot: RepositorySnapshot) -> list[str]:
        text = f"{issue.title} {issue.body}".lower()
        scored: list[tuple[int, str]] = []
        for file in snapshot.files:
            score = 0
            path_tokens = (
                file.path.lower().replace("/", " ").replace("_", " ").replace(".", " ").split()
            )
            score += sum(1 for token in path_tokens if len(token) > 2 and token in text)
            if file.is_entry_point:
                score += 1
            if file.is_test:
                score -= 1
            if score > 0:
                scored.append((score, file.path))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [path for _, path in scored[:8]]
