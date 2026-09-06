$ErrorActionPreference = "Stop"

Write-Host "Applying RedForge AI v1.2.0 consolidated full-platform upgrade..."

$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Destination = (Get-Location).Path

Get-ChildItem -Path $Source -Force | Where-Object {
    $_.Name -notin @(
        "APPLY_V120_FULL_PLATFORM.ps1",
        "TAG_V120_AFTER_MERGE.ps1"
    )
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $Destination -Recurse -Force
}

Write-Host ""
Write-Host "Upgrade copied."
Write-Host "Run:"
Write-Host '  python -m pip install -e ".[dev]"'
Write-Host "  python -m ruff format ."
Write-Host "  python -m ruff check ."
Write-Host "  python -m pytest -q"
Write-Host "  python -m mypy backend\redforge"
Write-Host "  python scripts\validate_v120_full.py"
Write-Host "  git diff --check"
