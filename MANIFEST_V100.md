# RedForge AI v1.0.0 Upgrade Overlay

Copy the contents of this archive into the repository root. Existing paths are intended to be overwritten; new paths are added.

Before applying, make sure the current feature branch is clean or create a backup/stash.

After extraction run:

```powershell
python -m pip install -e ".[dev]"
python -m ruff check . --fix
python -m ruff check .
python -m pytest -q
python -m mypy backend/redforge
```

Because Windows Application Control previously blocked local MyPy native components on this machine, treat a local MyPy launch failure caused by blocked DLLs separately from source type errors; CI should still run MyPy on Linux.
