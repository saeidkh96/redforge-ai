# RedForge AI v1.6.1 Maintenance Manifest

## Security and runtime hardening

- `backend/redforge/api/autonomy.py`
- `backend/redforge/roadmap_v200/webhook.py`
- `backend/redforge/core/config.py`
- `.env.example`

## Portability cleanup

- `backend/redforge/repository/dependencies.py`
- `backend/redforge/repository/symbols.py`
- `backend/redforge/roadmap_v140/intelligence.py`
- `backend/redforge/roadmap_v200/intelligence.py`
- `backend/redforge/security/scanner.py`
- `backend/redforge/verification/advanced.py`

## Tests and validation

- `tests/roadmap_v200/test_api.py`
- `tests/roadmap_v200/test_webhook.py`
- `scripts/validate_v161.py`
- `VALIDATE_V161_FULL.ps1`
- `.github/workflows/ci.yml`

## Release metadata and documentation

- `pyproject.toml`
- `backend/redforge/__init__.py`
- `tests/test_health.py`
- `tests/test_version.py`
- `README.md`
- `docs/releases/v1.6.1.md`

Removed obsolete staged roadmap: `docs/ROADMAP_V150_TO_V200.md`.
