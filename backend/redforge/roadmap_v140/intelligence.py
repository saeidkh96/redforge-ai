import ast
from collections import defaultdict, deque
from pathlib import Path

from redforge.roadmap_v140.models import DependencyEdge, ImpactReport


class PythonImpactAnalyzer:
    def build_edges(self, root: str | Path) -> list[DependencyEdge]:
        workspace = Path(root)
        edges: list[DependencyEdge] = []
        for path in workspace.rglob("*.py"):
            if any(part.startswith(".") for part in path.relative_to(workspace).parts):
                continue
            source = self._module_name(workspace, path)
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError, SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for item in node.names:
                        edges.append(DependencyEdge(source=source, target=item.name, kind="import"))
                elif isinstance(node, ast.ImportFrom) and node.module:
                    edges.append(
                        DependencyEdge(source=source, target=node.module, kind="from-import")
                    )
        return edges

    def analyze(self, root: str | Path, changed_files: list[str]) -> ImpactReport:
        workspace = Path(root)
        edges = self.build_edges(workspace)
        changed_modules = {
            self._module_name(workspace, workspace / changed)
            for changed in changed_files
            if (workspace / changed).suffix == ".py"
        }
        reverse: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            reverse[edge.target].add(edge.source)
        direct: set[str] = set()
        for module in changed_modules:
            direct.update(reverse.get(module, set()))
        transitive: set[str] = set()
        queue = deque(direct)
        seen = set(changed_modules) | direct
        while queue:
            current = queue.popleft()
            for dependent in reverse.get(current, set()):
                if dependent not in seen:
                    seen.add(dependent)
                    transitive.add(dependent)
                    queue.append(dependent)
        score = min(100.0, len(changed_files) * 3.0 + len(direct) * 7.0 + len(transitive) * 4.0)
        return ImpactReport(
            changed_files=changed_files,
            directly_impacted=sorted(direct),
            transitively_impacted=sorted(transitive),
            edges=edges,
            score=score,
        )

    @staticmethod
    def _module_name(root: Path, path: Path) -> str:
        relative = path.resolve().relative_to(root.resolve()).with_suffix("")
        parts = list(relative.parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts)
