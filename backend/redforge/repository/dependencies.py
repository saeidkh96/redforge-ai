from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class Dependency(BaseModel):
    name: str
    specifier: str = ""
    source: str
    group: str = "runtime"
    ecosystem: str


class DependencyInventory(BaseModel):
    ecosystems: list[str] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)


class DependencyInspector:
    def inspect(self, root: Path) -> DependencyInventory:
        dependencies: list[Dependency] = []

        dependencies.extend(self._pyproject(root / "pyproject.toml"))
        dependencies.extend(self._requirements(root / "requirements.txt"))
        dependencies.extend(self._package_json(root / "package.json"))
        dependencies.extend(self._cargo(root / "Cargo.toml"))
        dependencies.extend(self._go_mod(root / "go.mod"))

        ecosystems = sorted({item.ecosystem for item in dependencies})
        dependencies.sort(key=lambda item: (item.ecosystem, item.group, item.name.lower()))
        return DependencyInventory(ecosystems=ecosystems, dependencies=dependencies)

    @staticmethod
    def _split_python_requirement(requirement: str) -> tuple[str, str]:
        match = re.match(r"^([A-Za-z0-9_.-]+)(.*)$", requirement.strip())
        if not match:
            return requirement.strip(), ""
        return match.group(1), match.group(2).strip()

    def _pyproject(self, path: Path) -> list[Dependency]:
        if not path.is_file():
            return []
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except OSError, tomllib.TOMLDecodeError:
            return []

        result: list[Dependency] = []
        project = data.get("project", {})
        for requirement in project.get("dependencies", []) or []:
            name, specifier = self._split_python_requirement(str(requirement))
            result.append(
                Dependency(name=name, specifier=specifier, source=path.name, ecosystem="Python")
            )

        optional = project.get("optional-dependencies", {}) or {}
        for group, requirements in optional.items():
            for requirement in requirements or []:
                name, specifier = self._split_python_requirement(str(requirement))
                result.append(
                    Dependency(
                        name=name,
                        specifier=specifier,
                        source=path.name,
                        group=str(group),
                        ecosystem="Python",
                    )
                )
        return result

    def _requirements(self, path: Path) -> list[Dependency]:
        if not path.is_file():
            return []
        result: list[Dependency] = []
        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            name, specifier = self._split_python_requirement(line)
            result.append(
                Dependency(name=name, specifier=specifier, source=path.name, ecosystem="Python")
            )
        return result

    @staticmethod
    def _package_json(path: Path) -> list[Dependency]:
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except OSError, json.JSONDecodeError:
            return []
        result: list[Dependency] = []
        for key, group in (("dependencies", "runtime"), ("devDependencies", "dev")):
            for name, specifier in (data.get(key, {}) or {}).items():
                result.append(
                    Dependency(
                        name=name,
                        specifier=str(specifier),
                        source=path.name,
                        group=group,
                        ecosystem="Node.js",
                    )
                )
        return result

    @staticmethod
    def _cargo(path: Path) -> list[Dependency]:
        if not path.is_file():
            return []
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except OSError, tomllib.TOMLDecodeError:
            return []
        result: list[Dependency] = []
        for key, group in (("dependencies", "runtime"), ("dev-dependencies", "dev")):
            for name, value in (data.get(key, {}) or {}).items():
                specifier = value if isinstance(value, str) else str(value.get("version", ""))
                result.append(
                    Dependency(
                        name=name,
                        specifier=specifier,
                        source=path.name,
                        group=group,
                        ecosystem="Rust",
                    )
                )
        return result

    @staticmethod
    def _go_mod(path: Path) -> list[Dependency]:
        if not path.is_file():
            return []
        result: list[Dependency] = []
        in_block = False
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line == "require (":
                in_block = True
                continue
            if in_block and line == ")":
                in_block = False
                continue
            if line.startswith("require "):
                line = line.removeprefix("require ").strip()
            elif not in_block:
                continue
            parts = line.split()
            if len(parts) >= 2:
                result.append(
                    Dependency(
                        name=parts[0],
                        specifier=parts[1],
                        source=path.name,
                        ecosystem="Go",
                    )
                )
        return result
