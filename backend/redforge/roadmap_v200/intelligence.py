from __future__ import annotations

import ast
import re
from collections import defaultdict, deque
from pathlib import Path

from redforge.roadmap_v200.models import (
    CallRecord,
    DeepImpactReport,
    DependencyRecord,
    SymbolRecord,
)


class _PythonCollector(ast.NodeVisitor):
    def __init__(self, rel: str) -> None:
        self.rel = rel
        self.stack: list[str] = []
        self.dependencies: list[DependencyRecord] = []
        self.symbols: list[SymbolRecord] = []
        self.calls: list[CallRecord] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.dependencies.extend(
            DependencyRecord(source=self._module(), target=item.name, kind="import")
            for item in node.names
        )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.dependencies.append(
                DependencyRecord(source=self._module(), target=node.module, kind="from-import")
            )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._enter_symbol(node.name, "class", node.lineno, node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_symbol(node.name, "function", node.lineno, node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._enter_symbol(node.name, "function", node.lineno, node)

    def visit_Call(self, node: ast.Call) -> None:
        target = self._call_name(node.func)
        if target:
            self.calls.append(
                CallRecord(
                    source_path=self.rel,
                    source_symbol=".".join(self.stack) if self.stack else "<module>",
                    target_symbol=target,
                    line=getattr(node, "lineno", None),
                )
            )
        self.generic_visit(node)

    def _enter_symbol(self, name: str, kind: str, line: int, node: ast.AST) -> None:
        self.stack.append(name)
        self.symbols.append(
            SymbolRecord(
                path=self.rel,
                name=name,
                kind=kind,
                line=line,
                qualified_name=".".join(self.stack),
            )
        )
        self.generic_visit(node)
        self.stack.pop()

    def _module(self) -> str:
        value = self.rel[:-3] if self.rel.endswith(".py") else self.rel
        if value.endswith("/__init__"):
            value = value[: -len("/__init__")]
        return value.replace("/", ".")

    @staticmethod
    def _call_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            left = _PythonCollector._call_name(node.value)
            return f"{left}.{node.attr}" if left else node.attr
        return None


class DeepRepositoryAnalyzer:
    _JS_IMPORT = re.compile(r"""(?:from\s+|require\()(['"])([^'"]+)\1""")
    _JAVA_IMPORT = re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE)
    _C_INCLUDE = re.compile(r"""^\s*#include\s+[<"]([^>"]+)[>"]""", re.MULTILINE)

    def analyze(self, root: str | Path, changed_files: list[str]) -> DeepImpactReport:
        workspace = Path(root).resolve()
        dependencies: list[DependencyRecord] = []
        symbols: list[SymbolRecord] = []
        calls: list[CallRecord] = []

        for path in workspace.rglob("*"):
            if not path.is_file() or self._ignored(workspace, path):
                continue
            rel = path.relative_to(workspace).as_posix()
            if path.suffix == ".py":
                deps, found, found_calls = self._python(path, rel)
                dependencies.extend(deps)
                symbols.extend(found)
                calls.extend(found_calls)
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

        changed_keys = {item.replace("\\", "/") for item in changed_files}
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

        changed_stems = {Path(item).stem for item in changed_files}
        changed_symbols = sorted(
            {
                symbol.qualified_name or symbol.name
                for symbol in symbols
                if Path(symbol.path).stem in changed_stems
            }
        )
        impacted_symbols = sorted(
            {
                call.source_symbol
                for call in calls
                if any(
                    call.target_symbol == symbol or call.target_symbol.endswith(f".{symbol}")
                    for symbol in changed_symbols
                )
            }
        )

        tests = self._suggest_tests(workspace, changed_files, direct | transitive, impacted_symbols)
        score = min(
            100.0,
            4.0 * len(changed_files)
            + 6.0 * len(direct)
            + 3.0 * len(transitive)
            + 1.5 * len(impacted_symbols),
        )
        return DeepImpactReport(
            changed_files=changed_files,
            directly_impacted=sorted(direct),
            transitively_impacted=sorted(transitive),
            suggested_tests=tests,
            dependencies=dependencies,
            symbols=symbols,
            calls=calls,
            changed_symbols=changed_symbols,
            impacted_symbols=impacted_symbols,
            risk_score=score,
        )

    def _python(
        self, path: Path, rel: str
    ) -> tuple[list[DependencyRecord], list[SymbolRecord], list[CallRecord]]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError, SyntaxError:
            return [], [], []
        collector = _PythonCollector(rel)
        collector.visit(tree)
        return collector.dependencies, collector.symbols, collector.calls

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
        ignored = {".venv", "venv", "node_modules", "__pycache__", ".redforge", ".git"}
        return any(part in ignored for part in path.relative_to(root).parts)

    @staticmethod
    def _suggest_tests(
        root: Path,
        changed: list[str],
        impacted: set[str],
        impacted_symbols: list[str],
    ) -> list[str]:
        needles = {Path(item).stem.lower() for item in changed}
        needles.update(Path(item.replace(".", "/")).stem.lower() for item in impacted)
        needles.update(item.split(".")[-1].lower() for item in impacted_symbols)
        matches: list[str] = []
        all_tests: list[str] = []
        for path in root.rglob("test*.py"):
            rel = path.relative_to(root).as_posix()
            all_tests.append(rel)
            low = rel.lower()
            if any(needle and needle in low for needle in needles):
                matches.append(rel)
        return sorted(set(matches or all_tests[:25]))
