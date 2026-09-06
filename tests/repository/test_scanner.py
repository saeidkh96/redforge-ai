import subprocess
from pathlib import Path

import pytest
from redforge.repository import RepositoryScanner


def test_scanner_builds_repository_snapshot(tmp_path: Path) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".venv").mkdir()

    (tmp_path / "app" / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )
    (tmp_path / "app" / "service.py").write_text(
        "def run():\n    return True\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_service.py").write_text(
        "def test_run():\n    assert True\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='sample'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Sample",
        encoding="utf-8",
    )
    (tmp_path / ".venv" / "ignored.py").write_text(
        "print('ignore me')",
        encoding="utf-8",
    )

    scanner = RepositoryScanner()
    snapshot = scanner.scan(tmp_path)

    assert snapshot.name == tmp_path.name
    assert snapshot.total_files == 5

    assert snapshot.languages["Python"] == 3
    assert snapshot.languages["TOML"] == 1
    assert snapshot.languages["Markdown"] == 1

    assert "tests/test_service.py" in snapshot.test_files
    assert "pyproject.toml" in snapshot.config_files
    assert "app/main.py" in snapshot.entry_points

    scanned_paths = {file.path for file in snapshot.files}

    assert ".venv/ignored.py" not in scanned_paths


def test_scanner_rejects_missing_repository(tmp_path: Path) -> None:
    scanner = RepositoryScanner()

    missing_path = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        scanner.scan(missing_path)


def test_scanner_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("hello", encoding="utf-8")

    scanner = RepositoryScanner()

    with pytest.raises(NotADirectoryError):
        scanner.scan(file_path)


def test_scanner_detects_project_metadata(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "example"
dependencies = [
    "fastapi>=0.116.0",
]
""",
        encoding="utf-8",
    )

    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.14-slim",
        encoding="utf-8",
    )

    scanner = RepositoryScanner()
    snapshot = scanner.scan(tmp_path)

    assert "pyproject.toml" in snapshot.manifests

    assert snapshot.project_types == [
        "Docker",
        "Python",
    ]

    assert snapshot.frameworks == ["FastAPI"]

    assert "FastAPI" in snapshot.summary
    assert "Python" in snapshot.summary


def test_init_files_are_not_counted_as_tests(tmp_path: Path) -> None:
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()

    (tests_directory / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    (tests_directory / "test_example.py").write_text(
        "def test_example():\n    assert True\n",
        encoding="utf-8",
    )

    scanner = RepositoryScanner()
    snapshot = scanner.scan(tmp_path)

    assert "tests/test_example.py" in snapshot.test_files
    assert "tests/__init__.py" not in snapshot.test_files


def test_scanner_includes_git_metadata(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(tmp_path), "init"],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "RedForge Test"],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "config",
            "user.email",
            "redforge@example.com",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    (tmp_path / "main.py").write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "main.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "initial"],
        check=True,
        capture_output=True,
        text=True,
    )

    scanner = RepositoryScanner()
    snapshot = scanner.scan(tmp_path)

    assert snapshot.git is not None
    assert snapshot.git.is_repository is True
    assert snapshot.git.head_sha is not None
    assert snapshot.git.is_dirty is False
