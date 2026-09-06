from pathlib import Path

_MANIFEST_FILE_NAMES: set[str] = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "Gemfile",
}


def detect_manifests(paths: list[Path]) -> list[str]:
    return sorted(path.as_posix() for path in paths if path.name in _MANIFEST_FILE_NAMES)


def detect_project_types(paths: list[Path]) -> list[str]:
    file_names = {path.name for path in paths}
    suffixes = {path.suffix.lower() for path in paths}
    project_types: set[str] = set()
    if ".py" in suffixes or "pyproject.toml" in file_names:
        project_types.add("Python")
    if "package.json" in file_names:
        project_types.add("Node.js")
    if "Cargo.toml" in file_names:
        project_types.add("Rust")
    if "go.mod" in file_names:
        project_types.add("Go")
    if "pom.xml" in file_names or "build.gradle" in file_names:
        project_types.add("Java")
    if "Dockerfile" in file_names:
        project_types.add("Docker")
    return sorted(project_types)


def detect_frameworks(root: Path, paths: list[Path]) -> list[str]:
    frameworks: set[str] = set()
    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"
    package_json = root / "package.json"
    python_dependency_text = ""
    for dependency_file in (pyproject, requirements):
        if dependency_file.exists() and dependency_file.is_file():
            python_dependency_text += dependency_file.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
    if "fastapi" in python_dependency_text:
        frameworks.add("FastAPI")
    if "django" in python_dependency_text:
        frameworks.add("Django")
    if "flask" in python_dependency_text:
        frameworks.add("Flask")
    if package_json.exists() and package_json.is_file():
        package_text = package_json.read_text(encoding="utf-8", errors="ignore").lower()
        if '"react"' in package_text:
            frameworks.add("React")
        if '"next"' in package_text:
            frameworks.add("Next.js")
        if '"vue"' in package_text:
            frameworks.add("Vue")
        if '"express"' in package_text:
            frameworks.add("Express")
    if "manage.py" in {path.name for path in paths}:
        frameworks.add("Django")
    return sorted(frameworks)
