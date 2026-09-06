from pathlib import Path

from redforge.production import ProductionRuntime


def test_runtime_audit_chain_is_valid(tmp_path: Path) -> None:
    runtime = ProductionRuntime(tmp_path)
    evidence = runtime.evidence()
    assert evidence.audit_chain_valid is True
