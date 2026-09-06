import json
from pathlib import Path

from redforge.models import ForgeRun


class RunStore:
    def __init__(self, directory: str | Path = ".redforge/runs") -> None:
        self.directory = Path(directory)

    def save(self, run: ForgeRun) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{run.id}.json"
        path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, run_id: str) -> ForgeRun:
        path = self.directory / f"{run_id}.json"
        return ForgeRun.model_validate(json.loads(path.read_text(encoding="utf-8")))
