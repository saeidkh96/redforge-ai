from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from redforge.models import CommandResult, Finding, RiskLevel, VerificationReport
from redforge.production.sandbox import SandboxedCommandRunner
from redforge.security import SecurityScanner


@dataclass(slots=True)
class VerificationProfile:
    run_ruff: bool = True
    run_mypy: bool = True
    run_pytest: bool = True
    run_coverage: bool = True
    run_bandit: bool = True
    run_semgrep: bool = True
    minimum_coverage: float = 70.0
    regression_baseline: Path | None = None
    optional_tools: set[str] = field(default_factory=lambda: {"bandit", "semgrep"})


class AdvancedVerificationEngine:
    def __init__(
        self,
        runner: SandboxedCommandRunner,
        profile: VerificationProfile | None = None,
    ) -> None:
        self.runner = runner
        self.profile = profile or VerificationProfile()

    def verify(self, root: str | Path) -> VerificationReport:
        root_path = Path(root).resolve()
        commands: list[CommandResult] = []
        findings: list[Finding] = []

        checks: list[tuple[str, list[str], bool]] = []
        if self.profile.run_ruff:
            checks.append(("ruff", ["python", "-m", "ruff", "check", "."], False))
        if self.profile.run_mypy:
            checks.append(("mypy", ["python", "-m", "mypy", "backend", "redforge"], False))
        if self.profile.run_pytest:
            checks.append(("pytest", ["python", "-m", "pytest", "-q"], False))
        if self.profile.run_coverage:
            checks.append(
                (
                    "coverage",
                    [
                        "python",
                        "-m",
                        "pytest",
                        "--cov=backend/redforge",
                        "--cov-report=json",
                        "-q",
                    ],
                    False,
                )
            )
        if self.profile.run_bandit:
            checks.append(
                ("bandit", ["python", "-m", "bandit", "-r", "backend/redforge", "-q"], True)
            )
        if self.profile.run_semgrep:
            checks.append(
                (
                    "semgrep",
                    ["python", "-m", "semgrep", "scan", "--config", "auto", "backend/redforge"],
                    True,
                )
            )

        blocking_failure = False
        for name, command, optional in checks:
            result = self.runner.run(root_path, command)
            commands.append(result)
            unavailable = result.return_code != 0 and "No module named" in (
                result.stderr + result.stdout
            )
            if unavailable and optional:
                findings.append(
                    Finding(
                        source=name,
                        severity=RiskLevel.LOW,
                        message=f"Optional verification tool unavailable: {name}",
                        rule_id="tool.optional_unavailable",
                    )
                )
                continue
            if not result.passed:
                blocking_failure = True
                findings.append(
                    Finding(
                        source=name,
                        severity=RiskLevel.HIGH,
                        message=f"Verification command failed: {name}",
                        rule_id="verification.command_failed",
                    )
                )

        findings.extend(SecurityScanner().scan(root_path))

        if self.profile.run_coverage:
            coverage_path = root_path / "coverage.json"
            if coverage_path.exists():
                try:
                    data = json.loads(coverage_path.read_text(encoding="utf-8"))
                    percent = float(data["totals"]["percent_covered"])
                    if percent < self.profile.minimum_coverage:
                        blocking_failure = True
                        findings.append(
                            Finding(
                                source="coverage",
                                severity=RiskLevel.HIGH,
                                message=(
                                    f"Coverage {percent:.2f}% is below required "
                                    f"{self.profile.minimum_coverage:.2f}%."
                                ),
                                rule_id="coverage.minimum",
                            )
                        )
                except KeyError, ValueError, json.JSONDecodeError:
                    findings.append(
                        Finding(
                            source="coverage",
                            severity=RiskLevel.MEDIUM,
                            message="Coverage report could not be parsed.",
                            rule_id="coverage.parse_error",
                        )
                    )

        if self.profile.regression_baseline:
            baseline = self.profile.regression_baseline
            if baseline.exists():
                expected = {
                    line.strip()
                    for line in baseline.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                }
                current = {
                    finding.rule_id or finding.message
                    for finding in findings
                    if finding.severity in {RiskLevel.HIGH, RiskLevel.CRITICAL}
                }
                new_regressions = current - expected
                for regression in sorted(new_regressions):
                    blocking_failure = True
                    findings.append(
                        Finding(
                            source="regression",
                            severity=RiskLevel.HIGH,
                            message=f"New blocking regression: {regression}",
                            rule_id="regression.new",
                        )
                    )

        blocking_findings = any(
            finding.severity in {RiskLevel.HIGH, RiskLevel.CRITICAL} for finding in findings
        )
        return VerificationReport(
            commands=commands,
            findings=findings,
            passed=not blocking_failure and not blocking_findings,
        )
