from __future__ import annotations

import ast
from pathlib import Path

from pydantic import BaseModel, Field


class CodeSymbol(BaseModel):
    name: str
    kind: str
    path: str
    line: int


class SymbolIndex(BaseModel):
    symbols: list[CodeSymbol] = Field(default_factory=list)


class SymbolInspector:
    def inspect(self, root: Path, relative_paths: list[Path]) -> SymbolIndex:
        symbols: list[CodeSymbol] = []
        for relative in relative_paths:
            if relative.suffix.lower() != ".py":
                continue
            path = root / relative
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError, SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(
                        CodeSymbol(
                            name=node.name,
                            kind="function",
                            path=relative.as_posix(),
                            line=node.lineno,
                        )
                    )
                elif isinstance(node, ast.ClassDef):
                    symbols.append(
                        CodeSymbol(
                            name=node.name, kind="class", path=relative.as_posix(), line=node.lineno
                        )
                    )
        symbols.sort(key=lambda item: (item.path, item.line, item.name))
        return SymbolIndex(symbols=symbols)
