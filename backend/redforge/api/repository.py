from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from redforge.core.config import get_settings
from redforge.repository import RepositoryScanner, RepositorySnapshot

router = APIRouter(prefix="/api/v1/repository", tags=["repository"])


class RepositoryScanRequest(BaseModel):
    path: str


def _validate_workspace(path: Path) -> Path:
    resolved = path.resolve()
    allowed = get_settings().workspace_root
    if allowed is None:
        return resolved
    allowed_root = Path(allowed).resolve()
    try:
        resolved.relative_to(allowed_root)
    except ValueError as exc:
        raise HTTPException(
            status_code=403, detail="Repository path is outside the configured workspace root."
        ) from exc
    return resolved


@router.post("/scan", response_model=RepositorySnapshot)
def scan_repository(request: RepositoryScanRequest) -> RepositorySnapshot:
    scanner = RepositoryScanner()
    try:
        return scanner.scan(_validate_workspace(Path(request.path)))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
