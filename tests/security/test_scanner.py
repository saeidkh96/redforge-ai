from pathlib import Path

from redforge.security import SecurityScanner


def test_security_scanner_detects_eval(tmp_path: Path) -> None:
    (tmp_path / "danger.py").write_text("value = eval(user_input)\n", encoding="utf-8")
    findings = SecurityScanner().scan(tmp_path)
    assert any(item.rule_id == "python-eval" for item in findings)
