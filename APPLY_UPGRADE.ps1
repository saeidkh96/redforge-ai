$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Get-Location

Write-Host "Applying RedForge AI v1.0.0 overlay to $projectRoot"

Get-ChildItem -Path $packageRoot -Force | Where-Object {
    $_.Name -notin @("APPLY_UPGRADE.ps1", "MANIFEST_V100.md")
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $projectRoot -Recurse -Force
}

Write-Host "Overlay applied. Run the quality gates before committing."
