from pathlib import Path

from redforge.repository.dependencies import DependencyInspector


def test_pyproject_dependencies(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        (
            "[project]\n"
            'dependencies=["fastapi>=0.116", "pydantic"]\n'
            "[project.optional-dependencies]\n"
            'dev=["pytest>=8"]\n'
        ),
        encoding="utf-8",
    )

    inventory = DependencyInspector().inspect(tmp_path)

    assert inventory.ecosystems == ["Python"]
    assert {item.name for item in inventory.dependencies} == {
        "fastapi",
        "pydantic",
        "pytest",
    }
    assert next(item for item in inventory.dependencies if item.name == "pytest").group == "dev"


def test_package_json_dependencies(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        ('{"dependencies":{"react":"^19"},"devDependencies":{"vitest":"^3"}}'),
        encoding="utf-8",
    )

    inventory = DependencyInspector().inspect(tmp_path)

    assert inventory.ecosystems == ["Node.js"]
    assert [item.name for item in inventory.dependencies] == [
        "vitest",
        "react",
    ]
