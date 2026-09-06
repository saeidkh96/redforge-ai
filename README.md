<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

# RedForge AI

RedForge AI is an agentic software engineering platform designed around a verifiable workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Test → Repair → Security / Regression Check → Human Approval → Pull Request**

> **Generation proposes. Verification decides.**

## v1.1.0 — Automated Repair Loop

v1.1.0 upgrades the Repair Agent from a standalone contract into a bounded **Test → Repair → Retest** workflow.

When an applied AI-generated patch fails repository-native tests, RedForge can request a minimal repair patch, validate it with Git, apply it, rerun tests, and repeat only up to a configured attempt limit. Every repair attempt is persisted in the `ForgeRun` audit record.

Repair runs only when all of the following are true:

- patch generation is enabled,
- patch application is enabled,
- an LLM provider is configured,
- tests fail,
- repair-on-failure is enabled,
- the configured attempt limit has not been reached.

## Platform capabilities

- Repository intelligence: files, languages, manifests, frameworks, project types, Git state, dependency inventory, and Python symbol indexing.
- Deterministic issue planning with repository-aware target selection and risk notes.
- Provider-independent LLM gateway with an OpenAI-compatible adapter and deterministic test provider.
- Coding-agent contract that accepts structured JSON and produces a unified Git patch.
- Patch preflight and application through `git apply`.
- Repository-native test command detection and subprocess execution with timeouts.
- Bounded automated repair loop with persisted evidence.
- Deterministic security checks for risky Python execution patterns and likely hard-coded secrets.
- Verification engine combining quality/test commands with security findings.
- Risk-based human approval policy.
- Git workspace helpers and GitHub pull-request client.
- Persistent `ForgeRun` audit records.
- FastAPI endpoints for repository scanning and end-to-end forge runs.

## Quick start

```powershell
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python -m uvicorn redforge.main:app --app-dir backend --reload
```

Health endpoints:

- `GET /health`
- `GET /ready`

Repository intelligence:

- `POST /api/v1/repository/scan`

Forge workflow:

- `POST /api/v1/forge/runs`

## Repair configuration

```env
REDFORGE_REPAIR_ON_FAILURE=true
REDFORGE_MAX_REPAIR_ATTEMPTS=2
```

Per-run API overrides:

```json
{
  "generate_patch": true,
  "apply_patch": true,
  "repair_on_failure": true,
  "max_repair_attempts": 2
}
```

## LLM provider configuration

```env
REDFORGE_LLM_BASE_URL=http://localhost:11434/v1
REDFORGE_LLM_MODEL=qwen2.5-coder:7b
REDFORGE_LLM_API_KEY=
```

## Roadmap

The roadmap from **v1.1.0 through v2.0.0** is documented in `docs/ROADMAP_V2.md`.

The major direction is production hardening: advanced verification, sandboxed execution, runtime identity and permissions, egress controls, tamper-resistant audit evidence, reviewer reliability, multi-agent verification, GitHub workflow automation, and observability/scale.

Only capabilities implemented in the current release should be treated as shipped functionality.

## License

MIT
