from __future__ import annotations

import subprocess
from pathlib import Path

from redforge.models import Patch


class PatchApplyError(RuntimeError):
    pass


class PatchEngine:
    def check(self, root: str | Path, patch: Patch) -> None:
        self._apply(root, patch, check_only=True)

    def apply(self, root: str | Path, patch: Patch) -> None:
        self._apply(root, patch, check_only=False)

    @staticmethod
    def _apply(root: str | Path, patch: Patch, check_only: bool) -> None:
        repository = Path(root).resolve()
        args = ["git", "-C", str(repository), "apply", "--whitespace=error"]
        if check_only:
            args.append("--check")
        result = subprocess.run(
            args,
            input=patch.diff,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise PatchApplyError(
                result.stderr.strip() or result.stdout.strip() or "Patch could not be applied."
            )
