import subprocess
from pathlib import Path

from redforge.core import ForgeOrchestrator
from redforge.models import Issue
from redforge.persistence import RunStore


def test_orchestrator_reaches_verification_without_llm(tmp_path: Path) -> None:
    subprocess.run(["git", "-C", str(tmp_path), "init"], check=True, capture_output=True)
    (tmp_path / "example.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    store = RunStore(tmp_path / ".runs")
    run = ForgeOrchestrator(store=store).run(tmp_path, Issue(title="Document add function"))
    assert run.plan is not None
    assert run.verification is not None
    assert run.status in {"awaiting_approval", "completed"}
    assert (tmp_path / ".runs" / f"{run.id}.json").is_file()
