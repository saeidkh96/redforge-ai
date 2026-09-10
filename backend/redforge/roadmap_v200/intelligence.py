from __future__ import annotations

import ast
import re
from collections import defaultdict, deque
from pathlib import Path

from redforge.roadmap_v200.models import DeepImpactReport, DependencyRecord, SymbolRecord


class DeepRepositoryAnalyzer:
    _JS_IMPORT = re.compile(r"(?:from\s+|require\()(['\"])([^'\"]+)\1")
    _JAVA_IMPORT = re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE)
    _C_INCLUDE = re.compile(r"^\s*#include\s+[<\"]([^>\"]+)[>\"]", re.MULTILINE)

    def analyze(self, root: str | Path, changed_files: list[str]) -> DeepImpactReport:
        workspace = Path(root).resolve()
        dependencies: list[DependencyRecord] = []
        symbols: list[SymbolRecord] = []

        for path in workspace.rglob("*"):
            if not path.is_file() or self._ignored(workspace, path):
                continue
            rel = path.relative_to(workspace).as_posix()
            if path.suffix == ".py":
                deps, found = self._python(path, rel)
                dependencies.extend(deps)
                symbols.extend(found)
            elif path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
                dependencies.extend(self._regex_deps(path, rel, self._JS_IMPORT, "js-import", 2))
            elif path.suffix == ".java":
                dependencies.extend(
                    self._regex_deps(path, rel, self._JAVA_IMPORT, "java-import", 1)
                )
            elif path.suffix in {".c", ".cc", ".cpp", ".h", ".hpp"}:
                dependencies.extend(self._regex_deps(path, rel, self._C_INCLUDE, "include", 1))

        reverse: dict[str, set[str]] = defaultdict(set)
        for edge in dependencies:
            reverse[edge.target].add(edge.source)

        changed_keys = set(changed_files)
        changed_keys.update(
            self._module_from_path(item) for item in changed_files if item.endswith(".py")
        )
        direct: set[str] = set()
        for key in changed_keys:
            direct.update(reverse.get(key, set()))

        transitive: set[str] = set()
        queue = deque(direct)
        seen = set(changed_keys) | direct
        while queue:
            current = queue.popleft()
            for dependent in reverse.get(current, set()):
                if dependent not in seen:
                    seen.add(dependent)
                    transitive.add(dependent)
                    queue.append(dependent)

        tests = self._suggest_tests(workspace, changed_files, direct | transitive)
        score = min(100.0, 4.0 * len(changed_files) + 6.0 * len(direct) + 3.0 * len(transitive))
        return DeepImpactReport(
            changed_files=changed_files,
            directly_impacted=sorted(direct),
            transitively_impacted=sorted(transitive),
            suggested_tests=tests,
            dependencies=dependencies,
            symbols=symbols,
            risk_score=score,
        )

    def _python(self, path: Path, rel: str) -> tuple[list[DependencyRecord], list[SymbolRecord]]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError, SyntaxError:
            return [], []
        source = self._module_from_path(rel)
        deps: list[DependencyRecord] = []
        symbols: list[SymbolRecord] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                deps.extend(
                    DependencyRecord(source=source, target=item.name, kind="import")
                    for item in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                deps.append(DependencyRecord(source=source, target=node.module, kind="from-import"))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(
                    SymbolRecord(path=rel, name=node.name, kind="function", line=node.lineno)
                )
            elif isinstance(node, ast.ClassDef):
                symbols.append(
                    SymbolRecord(path=rel, name=node.name, kind="class", line=node.lineno)
                )
        return deps, symbols

    @staticmethod
    def _regex_deps(
        path: Path,
        rel: str,
        pattern: re.Pattern[str],
        kind: str,
        group: int,
    ) -> list[DependencyRecord]:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return []
        return [
            DependencyRecord(source=rel, target=match.group(group), kind=kind)
            for match in pattern.finditer(text)
        ]

    @staticmethod
    def _module_from_path(path: str) -> str:
        value = path.replace("\\", "/")
        if value.endswith(".py"):
            value = value[:-3]
        if value.endswith("/__init__"):
            value = value[: -len("/__init__")]
        return value.replace("/", ".")

    @staticmethod
    def _ignored(root: Path, path: Path) -> bool:
        ignored = {".venv", "venv", "node_modules", "__pycache__"}
        return any(part.startswith(".") or part in ignored for part in path.relative_to(root).parts)

    @staticmethod
    def _suggest_tests(root: Path, changed: list[str], impacted: set[str]) -> list[str]:
        needles = {Path(item).stem.lower() for item in changed}
        needles.update(Path(item.replace(".", "/")).stem.lower() for item in impacted)
        matches: list[str] = []
        for path in root.rglob("test*.py"):
            rel = path.relative_to(root).as_posix()
            low = rel.lower()
            if any(needle and needle in low for needle in needles):
                matches.append(rel)
        return sorted(set(matches))
