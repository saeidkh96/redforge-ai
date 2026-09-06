# RedForge AI v1.2.0

**Agentic Software Engineering Platform with runtime enforcement and verifiable autonomy.**

> **Generation proposes. Verification decides.**

RedForge AI v1.2.0 consolidates the previously planned v1.2.0 → v2.0.0
capability roadmap into one release while keeping the public release version at
**1.2.0**.

## Workflow

**Issue → Repository Understanding → Plan → Code → Test → Repair → Advanced Verification → Runtime Policy → Human Gate → Audit → Pull Request**

## Consolidated capabilities

- Bounded Test → Repair → Retest loop
- Ruff, MyPy, pytest, coverage and optional Bandit/Semgrep verification
- Regression-baseline checking
- Workspace-bound command execution
- Command allow-list and sanitized subprocess environment
- Runtime principals and explicit permissions
- Egress allow-list policy
- Sensitive-path human approval gate
- Hash-chained tamper-evident audit log
- Reviewer FP/FN and reliability scoring
- Independent multi-agent consensus
- Git/GitHub publishing workflow primitive
- Runtime metrics
- Concurrent job manager
- Unified `ProductionRuntime`

## Version

```text
1.2.0
```

The original roadmap milestone numbering remains documented for traceability,
but the functionality is consolidated into this v1.2.0 release.

## Validation

```powershell
python -m pip install -e ".[dev]"
python -m ruff format .
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python scripts\validate_v120_full.py
git diff --check
```

## Isolation note

The RedForge execution guard provides application-level workspace, command,
environment, timeout and authorization controls. Hostile/untrusted code should
still execute within a container, VM or equivalent OS-level sandbox.

## License

MIT
