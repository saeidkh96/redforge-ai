$ErrorActionPreference = "Stop"

git checkout main
git pull origin main
git tag -a v1.1.0 -m "RedForge AI v1.1.0"
git push origin v1.1.0
