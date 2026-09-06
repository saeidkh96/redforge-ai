# RedForge AI v1.1.0 Upgrade Manifest

This overlay upgrades a validated RedForge AI v1.0.0 checkout to the v1.1.0 Automated Repair Loop milestone and adds the full roadmap through v2.0.0.

## Runtime changes

- Version bumped to 1.1.0.
- `ForgeRun` now persists `repair_attempts`.
- Added `REPAIRING` and `REPAIRED` statuses.
- Automated bounded Test → Repair → Retest loop.
- Per-run/config-level repair controls.
- Repair prompt tightened to minimal demonstrated failure scope.

## New validation

- Repair-agent structured-output test.
- Repair-loop stop-on-pass test.
- v1.1.0 validation script.

## Roadmap

`docs/ROADMAP_V2.md` defines milestones from v1.1.0 through v2.0.0. Only v1.1.0 is implemented by this overlay; later milestones remain roadmap items and must not be claimed as implemented.
