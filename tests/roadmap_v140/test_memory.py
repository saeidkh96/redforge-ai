from pathlib import Path

from redforge.roadmap_v140 import EngineeringMemory


def test_engineering_memory_roundtrip(tmp_path: Path) -> None:
    memory = EngineeringMemory(tmp_path / "memory.sqlite3")
    memory.put(
        "failure-1", {"cause": "type mismatch"}, namespace="repairs", tags=["mypy", "repair"]
    )
    assert memory.get("failure-1", namespace="repairs").value["cause"] == "type mismatch"
    assert len(memory.search("mypy")) == 1
