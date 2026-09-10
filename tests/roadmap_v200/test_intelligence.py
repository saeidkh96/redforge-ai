from pathlib import Path

from redforge.roadmap_v200 import DeepRepositoryAnalyzer


def test_deep_repository_analyzer(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("import a\n", encoding="utf-8")
    (tmp_path / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
    report = DeepRepositoryAnalyzer().analyze(tmp_path, ["a.py"])
    assert "b" in report.directly_impacted
    assert any(item.name == "value" for item in report.symbols)
    assert "test_a.py" in report.suggested_tests
