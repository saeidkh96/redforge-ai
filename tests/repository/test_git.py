import subprocess
from pathlib import Path

from redforge.repository.git import GitInspector


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_git_inspector_detects_non_git_directory(
    tmp_path: Path,
) -> None:
    inspector = GitInspector()

    metadata = inspector.inspect(tmp_path)

    assert metadata.is_repository is False
    assert metadata.branch is None
    assert metadata.head_sha is None
    assert metadata.remotes == {}


def test_git_inspector_reads_repository_metadata(
    tmp_path: Path,
) -> None:
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.name", "RedForge Test")
    run_git(
        tmp_path,
        "config",
        "user.email",
        "redforge@example.com",
    )

    example_file = tmp_path / "example.py"
    example_file.write_text(
        "print('redforge')\n",
        encoding="utf-8",
    )

    run_git(tmp_path, "add", "example.py")
    run_git(tmp_path, "commit", "-m", "initial commit")

    inspector = GitInspector()
    metadata = inspector.inspect(tmp_path)

    assert metadata.is_repository is True
    assert metadata.branch is not None
    assert metadata.head_sha is not None
    assert metadata.is_dirty is False
    assert metadata.is_detached is False

    assert len(metadata.recent_commits) == 1
    assert metadata.recent_commits[0].author == "RedForge Test"
    assert metadata.recent_commits[0].message == "initial commit"

    example_file.write_text(
        "print('changed')\n",
        encoding="utf-8",
    )

    dirty_metadata = inspector.inspect(tmp_path)

    assert dirty_metadata.is_dirty is True
