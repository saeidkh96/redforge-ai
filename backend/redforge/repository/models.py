from pathlib import Path

from pydantic import BaseModel, Field

from redforge.repository.dependencies import DependencyInventory
from redforge.repository.git import GitMetadata
from redforge.repository.symbols import SymbolIndex


class RepositoryFile(BaseModel):
    path: str
    extension: str | None = None
    language: str | None = None
    size_bytes: int = 0
    is_test: bool = False
    is_config: bool = False
    is_entry_point: bool = False


class RepositorySnapshot(BaseModel):
    root: str
    name: str
    files: list[RepositoryFile] = Field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    languages: dict[str, int] = Field(default_factory=dict)
    test_files: list[str] = Field(default_factory=list)
    config_files: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    manifests: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    project_types: list[str] = Field(default_factory=list)
    git: GitMetadata | None = None
    dependencies: DependencyInventory = Field(default_factory=DependencyInventory)
    symbols: SymbolIndex = Field(default_factory=SymbolIndex)
    summary: str = ""

    @classmethod
    def empty(cls, root: Path) -> RepositorySnapshot:
        return cls(root=str(root), name=root.name)
