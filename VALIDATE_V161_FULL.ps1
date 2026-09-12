$ErrorActionPreference = "Stop"

python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy backend\redforge
python -m pytest -q
python scripts\validate_v161.py
git diff --check
git status

Write-Host ""
Write-Host "RedForge AI v1.6.1 validation completed." -ForegroundColor Green
