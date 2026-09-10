from pathlib import Path

import pytest
from redforge.roadmap_v200 import ReleaseGateEvaluator, SecretRedactor, WorkspaceBoundary


def test_release_gate_is_fail_closed() -> None:
    gate = ReleaseGateEvaluator().evaluate({})
    assert not gate.passed
    assert gate.reasons


def test_secret_redaction() -> None:
    assert "supersecretvalue" not in SecretRedactor().redact("api_key=supersecretvalue")


def test_workspace_boundary(tmp_path: Path) -> None:
    guard = WorkspaceBoundary(tmp_path)
    assert guard.require_inside(tmp_path / "x") == (tmp_path / "x").resolve()
    with pytest.raises(PermissionError):
        guard.require_inside(tmp_path.parent / "outside")
