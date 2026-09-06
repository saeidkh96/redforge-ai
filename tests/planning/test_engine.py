from redforge.models import Issue
from redforge.planning import PlanningEngine
from redforge.repository.models import RepositoryFile, RepositorySnapshot


def test_planner_creates_deterministic_plan() -> None:
    snapshot = RepositorySnapshot(
        root="/tmp/example",
        name="example",
        files=[RepositoryFile(path="backend/auth.py", language="Python")],
        test_files=["tests/test_auth.py"],
    )
    plan = PlanningEngine().create_plan(Issue(title="Fix auth token validation"), snapshot)
    assert len(plan.steps) == 3
    assert "backend/auth.py" in plan.steps[0].target_files
