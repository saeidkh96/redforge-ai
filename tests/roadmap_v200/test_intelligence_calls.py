from pathlib import Path

from redforge.roadmap_v200.intelligence import DeepRepositoryAnalyzer


def test_python_call_graph_and_symbol_impact(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text(
        "def target():\n    return 1\n\ndef caller():\n    return target()\n",
        encoding="utf-8",
    )
    report = DeepRepositoryAnalyzer().analyze(tmp_path, ["a.py"])
    assert any(call.target_symbol == "target" for call in report.calls)
    assert "target" in report.changed_symbols
    assert "caller" in report.changed_symbols
