from __future__ import annotations

import subprocess
from pathlib import Path


class GitWorkspace:
    def create_branch(self, root: str | Path, branch: str) -> None:
        self._run(root, "checkout", "-b", branch)

    def status(self, root: str | Path) -> str:
        return self._run(root, "status", "--short")

    def commit(self, root: str | Path, message: str) -> str:
        self._run(root, "add", "-A")
        self._run(root, "commit", "-m", message)
        return self._run(root, "rev-parse", "HEAD")

    @staticmethod
    def _run(root: str | Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(Path(root).resolve()), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Git command failed.")
        return result.stdout.strip()
