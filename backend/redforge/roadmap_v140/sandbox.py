from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from time import perf_counter

from redforge.roadmap_v140.models import (
    ExecutionMode,
    SandboxLimits,
    SandboxResult,
)


class DockerSandbox:
    def __init__(
        self,
        *,
        image: str = "python:3.14-slim",
        limits: SandboxLimits | None = None,
    ) -> None:
        self.image = image
        self.limits = limits or SandboxLimits()

    def available(self) -> bool:
        return shutil.which("docker") is not None

    def build_command(
        self,
        workspace: str | Path,
        command: list[str],
    ) -> list[str]:
        root = Path(workspace).resolve()
        network = "bridge" if self.limits.network_enabled else "none"
        result = [
            "docker",
            "run",
            "--rm",
            "--network",
            network,
            "--cpus",
            str(self.limits.cpus),
            "--memory",
            f"{self.limits.memory_mb}m",
            "--workdir",
            "/workspace",
            "--mount",
            f"type=bind,source={root},target=/workspace",
        ]

        if self.limits.read_only_root:
            result.extend(
                [
                    "--read-only",
                    "--tmpfs",
                    "/tmp:rw,noexec,nosuid,size=256m",
                ]
            )

        return result + [self.image] + command

    def run(
        self,
        workspace: str | Path,
        command: list[str],
        *,
        dry_run: bool = False,
    ) -> SandboxResult:
        docker_command = self.build_command(workspace, command)

        if dry_run:
            return SandboxResult(
                command=docker_command,
                return_code=0,
                mode=ExecutionMode.DOCKER,
            )

        if not self.available():
            raise RuntimeError("Docker is not available on PATH.")

        started = perf_counter()
        try:
            completed = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=self.limits.timeout_seconds,
                check=False,
            )
            return SandboxResult(
                command=docker_command,
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=perf_counter() - started,
                mode=ExecutionMode.DOCKER,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = (
                exc.stdout.decode(errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            )
            stderr = (
                exc.stderr.decode(errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            )
            return SandboxResult(
                command=docker_command,
                return_code=124,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=perf_counter() - started,
                timed_out=True,
                mode=ExecutionMode.DOCKER,
            )
