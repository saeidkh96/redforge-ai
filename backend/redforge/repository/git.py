import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class GitCommit(BaseModel):
    sha: str
    author: str
    message: str


class GitMetadata(BaseModel):
    is_repository: bool
    branch: str | None = None
    head_sha: str | None = None
    is_dirty: bool = False
    is_detached: bool = False
    remotes: dict[str, str] = Field(default_factory=dict)
    recent_commits: list[GitCommit] = Field(default_factory=list)


class GitInspector:
    def inspect(self, repository_path: str | Path) -> GitMetadata:
        root = Path(repository_path).resolve()
        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")
        if not self._is_git_repository(root):
            return GitMetadata(is_repository=False)
        branch = self._run(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        head_sha = self._run(root, "rev-parse", "HEAD", check=False) or None
        status = self._run(root, "status", "--porcelain")
        return GitMetadata(
            is_repository=True,
            branch=branch or None,
            head_sha=head_sha,
            is_dirty=bool(status),
            is_detached=not bool(branch),
            remotes=self._read_remotes(root),
            recent_commits=self._read_recent_commits(root),
        )

    def _is_git_repository(self, root: Path) -> bool:
        return self._run(root, "rev-parse", "--is-inside-work-tree", check=False) == "true"

    def _read_remotes(self, root: Path) -> dict[str, str]:
        names = self._run(root, "remote", check=False)
        if not names:
            return {}
        remotes: dict[str, str] = {}
        for name in names.splitlines():
            url = self._run(root, "remote", "get-url", name, check=False)
            if url:
                remotes[name] = url
        return remotes

    def _read_recent_commits(self, root: Path, limit: int = 5) -> list[GitCommit]:
        output = self._run(root, "log", f"-{limit}", "--pretty=format:%H%x1f%an%x1f%s", check=False)
        if not output:
            return []
        commits: list[GitCommit] = []
        for line in output.splitlines():
            parts = line.split("\x1f", maxsplit=2)
            if len(parts) == 3:
                sha, author, message = parts
                commits.append(GitCommit(sha=sha, author=author, message=message))
        return commits

    @staticmethod
    def _run(root: Path, *args: str, check: bool = True) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(root), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git executable was not found.") from exc
        if check and result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Git command failed.")
        return "" if result.returncode != 0 else result.stdout.strip()
