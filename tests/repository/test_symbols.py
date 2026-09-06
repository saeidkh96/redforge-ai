from pathlib import Path

from redforge.repository.symbols import SymbolInspector


def test_python_symbol_index(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("class Engine:\n    pass\n\ndef run():\n    return True\n", encoding="utf-8")
    index = SymbolInspector().inspect(tmp_path, [Path("module.py")])
    assert [(item.name, item.kind) for item in index.symbols] == [
        ("Engine", "class"),
        ("run", "function"),
    ]
