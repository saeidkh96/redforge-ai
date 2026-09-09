from pathlib import Path

from redforge.roadmap_v140 import CheckpointStore, ForgeGraph, GraphCheckpoint


def test_graph_runs_and_checkpoints(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    graph = ForgeGraph(checkpoint_store=store)
    graph.add_node("a", lambda state: {"value": state.get("value", 0) + 1})
    graph.add_node("b", lambda state: {"value": state["value"] + 1})
    graph.set_entry("a")
    graph.add_edge("a", "b")
    result = graph.run(GraphCheckpoint(run_id="run-1", state={}))
    assert result.completed is True
    assert result.state["value"] == 2
    assert store.exists("run-1")
