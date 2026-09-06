from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from redforge.models import CommandResult, TestRun
from redforge.repository import RepositorySnapshot


class TestRunner:
    def detect_commands(self, snapshot: RepositorySnapshot) -> list[list[str]]:
        root_files = {file.path for file in snapshot.files}
        commands: list[list[str]] = []

        if "pyproject.toml" in root_files or "requirements.txt" in root_files:
            commands.append(["python", "-m", "pytest", "-q"])

        if "package.json" in root_files:
            commands.append(["npm", "test", "--", "--runInBand"])

        if "Cargo.toml" in root_files:
            commands.append(["cargo", "test", "--quiet"])

        if "go.mod" in root_files:
            commands.append(["go", "test", "./..."])

        return commands

    def run(
        self,
        root: str | Path,
        snapshot: RepositorySnapshot,
        timeout: int = 300,
    ) -> TestRun:
        results = [
            self.run_command(root, command, timeout=timeout)
            for command in self.detect_commands(snapshot)
        ]
        return TestRun(results=results)

    @staticmethod
    def run_command(
        root: str | Path,
        command: list[str],
        timeout: int = 300,
    ) -> CommandResult:
        started = time.perf_counter()

        resolved_command = list(command)

        if resolved_command and resolved_command[0].lower() in {
            "python",
            "python3",
            "python.exe",
        }:
            resolved_command[0] = sys.executable

        try:
            result = subprocess.run(
                resolved_command,
                cwd=Path(root),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )

            return CommandResult(
                command=resolved_command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_seconds=time.perf_counter() - started,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                command=resolved_command,
                return_code=124,
                stdout=TestRunner._to_text(exc.stdout),
                stderr=TestRunner._to_text(exc.stderr),
                duration_seconds=time.perf_counter() - started,
                timed_out=True,
            )
        except FileNotFoundError as exc:
            return CommandResult(
                command=resolved_command,
                return_code=127,
                stderr=str(exc),
                duration_seconds=time.perf_counter() - started,
            )

    @staticmethod
    def _to_text(value: bytes | str | None) -> str:
        if value is None:
            return ""

        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")

        return value
