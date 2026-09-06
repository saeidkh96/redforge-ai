from pathlib import Path

from redforge.repository.dependencies import DependencyInspector
from redforge.repository.detectors import (
    detect_frameworks,
    detect_manifests,
    detect_project_types,
)
from redforge.repository.git import GitInspector
from redforge.repository.ignore import should_ignore
from redforge.repository.languages import detect_language
from redforge.repository.models import RepositoryFile, RepositorySnapshot
from redforge.repository.symbols import SymbolInspector

_CONFIG_FILE_NAMES: set[str] = {
    ".editorconfig",
    ".env",
    ".env.example",
    ".gitignore",
    "docker-compose.yaml",
    "docker-compose.yml",
    "Dockerfile",
    "Makefile",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "tsconfig.json",
}

_ENTRY_POINT_NAMES: set[str] = {
    "app.py",
    "main.py",
    "manage.py",
    "server.py",
    "index.js",
    "index.ts",
}


class RepositoryScanner:
    def scan(self, repository_path: str | Path) -> RepositorySnapshot:
        root = Path(repository_path).resolve()

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        snapshot = RepositorySnapshot.empty(root)
        discovered_paths: list[Path] = []

        for path in root.rglob("*"):
            if not path.is_file() or should_ignore(path, root):
                continue

            relative = path.relative_to(root)
            discovered_paths.append(relative)

            repository_file = self._build_repository_file(
                path=path,
                root=root,
            )
            snapshot.files.append(repository_file)
            snapshot.total_files += 1
            snapshot.total_size_bytes += repository_file.size_bytes

            if repository_file.language is not None:
                snapshot.languages[repository_file.language] = (
                    snapshot.languages.get(repository_file.language, 0) + 1
                )

            if repository_file.is_test:
                snapshot.test_files.append(repository_file.path)

            if repository_file.is_config:
                snapshot.config_files.append(repository_file.path)

            if repository_file.is_entry_point:
                snapshot.entry_points.append(repository_file.path)

        snapshot.files.sort(key=lambda item: item.path)
        snapshot.test_files.sort()
        snapshot.config_files.sort()
        snapshot.entry_points.sort()

        snapshot.manifests = detect_manifests(discovered_paths)
        snapshot.project_types = detect_project_types(discovered_paths)
        snapshot.frameworks = detect_frameworks(root, discovered_paths)
        snapshot.git = GitInspector().inspect(root)
        snapshot.dependencies = DependencyInspector().inspect(root)
        snapshot.symbols = SymbolInspector().inspect(root, discovered_paths)
        snapshot.summary = self._build_summary(snapshot)

        return snapshot

    def _build_repository_file(
        self,
        path: Path,
        root: Path,
    ) -> RepositoryFile:
        return RepositoryFile(
            path=path.relative_to(root).as_posix(),
            extension=path.suffix.lower() or None,
            language=detect_language(path),
            size_bytes=path.stat().st_size,
            is_test=self._is_test_file(path),
            is_config=self._is_config_file(path),
            is_entry_point=self._is_entry_point(path),
        )

    @staticmethod
    def _is_test_file(path: Path) -> bool:
        name = path.name.lower()
        parts = {part.lower() for part in path.parts}

        if name == "__init__.py":
            return False

        return (
            "tests" in parts
            or "test" in parts
            or name.startswith("test_")
            or name.endswith("_test.py")
            or name.endswith(".test.js")
            or name.endswith(".test.ts")
            or name.endswith(".spec.js")
            or name.endswith(".spec.ts")
        )

    @staticmethod
    def _is_config_file(path: Path) -> bool:
        return path.name in _CONFIG_FILE_NAMES

    @staticmethod
    def _is_entry_point(path: Path) -> bool:
        return path.name in _ENTRY_POINT_NAMES

    @staticmethod
    def _build_summary(snapshot: RepositorySnapshot) -> str:
        languages = ", ".join(
            f"{language} ({count})" for language, count in sorted(snapshot.languages.items())
        )
        frameworks = ", ".join(snapshot.frameworks) or "none detected"
        project_types = ", ".join(snapshot.project_types) or "unknown"

        return (
            f"{snapshot.name}: {snapshot.total_files} files; "
            f"project types: {project_types}; "
            f"frameworks: {frameworks}; "
            f"languages: {languages}; "
            f"tests: {len(snapshot.test_files)}; "
            f"dependencies: {len(snapshot.dependencies.dependencies)}; "
            f"symbols: {len(snapshot.symbols.symbols)}."
        )
