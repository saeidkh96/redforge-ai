$ErrorActionPreference = "Stop"

git switch main
git pull origin main
git tag -a v1.2.0 -m "RedForge AI v1.2.0 — Consolidated Production Platform"
git push origin v1.2.0
