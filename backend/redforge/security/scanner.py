from __future__ import annotations

import ast
import re
from pathlib import Path

from redforge.models import Finding, RiskLevel
from redforge.repository.ignore import should_ignore

_SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]")

_SCAN_TEXT_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".env",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}


class SecurityScanner:
    def scan(self, root: str | Path) -> list[Finding]:
        repository = Path(root).resolve()
        findings: list[Finding] = []

        for path in repository.rglob("*"):
            if not path.is_file() or should_ignore(path, repository):
                continue

            if path.suffix.lower() == ".py":
                findings.extend(self._scan_python(repository, path))

            if path.suffix.lower() in _SCAN_TEXT_SUFFIXES:
                findings.extend(self._scan_secrets(repository, path))

        return findings

    @staticmethod
    def _scan_python(root: Path, path: Path) -> list[Finding]:
        try:
            tree = ast.parse(
                path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )
        except OSError, SyntaxError:
            return []

        findings: list[Finding] = []
        relative = path.relative_to(root).as_posix()

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in {"eval", "exec"}
            ):
                findings.append(
                    Finding(
                        source="security",
                        severity=RiskLevel.HIGH,
                        message=(f"Use of {node.func.id}() requires manual review."),
                        path=relative,
                        line=node.lineno,
                        rule_id=f"python-{node.func.id}",
                    )
                )

            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"run", "Popen", "call"}
            ):
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        findings.append(
                            Finding(
                                source="security",
                                severity=RiskLevel.HIGH,
                                message=(
                                    "subprocess execution with shell=True requires manual review."
                                ),
                                path=relative,
                                line=node.lineno,
                                rule_id="python-shell-true",
                            )
                        )

        return findings

    @staticmethod
    def _scan_secrets(root: Path, path: Path) -> list[Finding]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        relative = path.relative_to(root).as_posix()
        findings: list[Finding] = []

        for line_number, line in enumerate(text.splitlines(), start=1):
            if _SECRET_PATTERN.search(line):
                findings.append(
                    Finding(
                        source="security",
                        severity=RiskLevel.CRITICAL,
                        message="Possible hard-coded secret detected.",
                        path=relative,
                        line=line_number,
                        rule_id="hardcoded-secret",
                    )
                )

        return findings
