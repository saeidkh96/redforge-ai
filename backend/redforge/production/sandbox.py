from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from redforge.models import CommandResult
from redforge.production.models import Decision, Permission, Principal, RuntimeAction
from redforge.production.policy import AuthorizationEngine


class SandboxedCommandRunner:
    """Policy-enforced subprocess runner.

    This provides a portable workspace boundary, command allow-list,
    sanitized environment and timeout enforcement. It is intentionally
    separate from OS/container isolation, which can be layered underneath.
    """

    def __init__(
        self,
        authorization: AuthorizationEngine,
        principal: Principal,
        *,
        timeout_seconds: int = 120,
    ) -> None:
        self.authorization = authorization
        self.principal = principal
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _resolve_command(command: list[str]) -> list[str]:
        resolved = list(command)
        if resolved and resolved[0].lower() in {"python", "python3", "python.exe"}:
            resolved[0] = sys.executable
        return resolved

    @staticmethod
    def _sanitized_env() -> dict[str, str]:
        keep = {
            "PATH",
            "PATHEXT",
            "SYSTEMROOT",
            "WINDIR",
            "TEMP",
            "TMP",
            "HOME",
            "USERPROFILE",
            "VIRTUAL_ENV",
            "PYTHONPATH",
            "LANG",
        }
        return {key: value for key, value in os.environ.items() if key in keep}

    def run(self, root: str | Path, command: list[str]) -> CommandResult:
        root_path = Path(root).resolve()
        resolved = self._resolve_command(command)
        action = RuntimeAction(
            action="execute_command",
            permission=Permission.EXECUTE_COMMAND,
            resource=str(root_path),
            metadata={"command": " ".join(resolved)},
        )
        decision = self.authorization.evaluate(self.principal, action)
        if decision.decision != Decision.ALLOW:
            return CommandResult(
                command=resolved,
                return_code=126,
                stderr=decision.reason,
            )

        started = perf_counter()
        try:
            completed = subprocess.run(
                resolved,
                cwd=root_path,
                env=self._sanitized_env(),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            return CommandResult(
                command=resolved,
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=perf_counter() - started,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                command=resolved,
                return_code=124,
                stdout=self._text(exc.stdout),
                stderr=self._text(exc.stderr),
                duration_seconds=perf_counter() - started,
                timed_out=True,
            )

    @staticmethod
    def _text(value: bytes | str | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value
