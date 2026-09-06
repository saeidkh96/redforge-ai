from pathlib import Path

IGNORED_DIRECTORY_NAMES: set[str] = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "venv",
    ".redforge",
}
IGNORED_FILE_NAMES: set[str] = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES: set[str] = {".pyc", ".pyo", ".class"}


def should_ignore(path: Path, root: Path) -> bool:
    relative_path = path.relative_to(root)
    if any(part in IGNORED_DIRECTORY_NAMES for part in relative_path.parts[:-1]):
        return True
    if path.name in IGNORED_FILE_NAMES:
        return True
    return path.suffix.lower() in IGNORED_SUFFIXES
