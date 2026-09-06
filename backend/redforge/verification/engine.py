from pathlib import Path

from redforge.execution.tests import TestRunner
from redforge.models import RiskLevel, VerificationReport
from redforge.security import SecurityScanner


class VerificationEngine:
    def verify(self, root: str | Path) -> VerificationReport:
        repository = Path(root).resolve()
        commands = []
        pyproject = repository / "pyproject.toml"
        if pyproject.is_file():
            commands.append(
                TestRunner.run_command(
                    repository, ["python", "-m", "ruff", "check", "."], timeout=180
                )
            )
            commands.append(
                TestRunner.run_command(repository, ["python", "-m", "pytest", "-q"], timeout=300)
            )
        findings = SecurityScanner().scan(repository)
        blocking = any(item.severity in {RiskLevel.HIGH, RiskLevel.CRITICAL} for item in findings)
        commands_passed = all(item.passed for item in commands) if commands else True
        return VerificationReport(
            commands=commands, findings=findings, passed=commands_passed and not blocking
        )
