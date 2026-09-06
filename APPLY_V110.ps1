$ErrorActionPreference = "Stop"

Write-Host "RedForge AI v1.1.0 upgrade validation" -ForegroundColor Cyan
python -m pip install -e ".[dev]"
python -m ruff format .
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python scripts\validate_v110.py
git diff --check

Write-Host "Local v1.1.0 validation completed. Do not tag until PR/CI/merge are complete." -ForegroundColor Green
