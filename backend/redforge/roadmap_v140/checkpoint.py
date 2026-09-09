import json
from pathlib import Path

from redforge.roadmap_v140.models import GraphCheckpoint


class CheckpointStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.directory = self.root / ".redforge" / "checkpoints"
        self.directory.mkdir(parents=True, exist_ok=True)

    def path_for(self, run_id: str) -> Path:
        return self.directory / f"{run_id}.json"

    def save(self, checkpoint: GraphCheckpoint) -> Path:
        path = self.path_for(checkpoint.run_id)
        path.write_text(checkpoint.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, run_id: str) -> GraphCheckpoint:
        return GraphCheckpoint.model_validate(
            json.loads(self.path_for(run_id).read_text(encoding="utf-8"))
        )

    def exists(self, run_id: str) -> bool:
        return self.path_for(run_id).exists()
