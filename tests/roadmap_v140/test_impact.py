from pathlib import Path

from redforge.roadmap_v140 import PythonImpactAnalyzer


def test_python_impact_analyzer_finds_direct_dependents(tmp_path: Path) -> None:
    (tmp_path / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "service.py").write_text("import core\n", encoding="utf-8")
    report = PythonImpactAnalyzer().analyze(tmp_path, ["core.py"])
    assert "service" in report.directly_impacted
    assert report.score > 0
