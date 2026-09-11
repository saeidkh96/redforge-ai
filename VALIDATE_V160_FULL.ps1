$ErrorActionPreference = "Stop"

python -m pip install -e ".[dev]"
python -m ruff format .
python -m ruff check .
python -m mypy backend\redforge
python -m pytest -q
python scripts\validate_v160.py
git diff --check
git status

Write-Host ""
Write-Host "RedForge AI v1.6.0 validation completed." -ForegroundColor Green
