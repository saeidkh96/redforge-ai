<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

# RedForge AI

RedForge AI is an agentic software engineering platform designed around a verifiable workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Test → Repair → Security / Regression Check → Human Approval → Pull Request**

## v1.0.0 capabilities

- Repository intelligence: files, languages, manifests, frameworks, project types, Git state, dependency inventory, and Python symbol indexing.
- Deterministic issue planning with repository-aware target selection and risk notes.
- Provider-independent LLM gateway with an OpenAI-compatible adapter and deterministic test provider.
- Coding-agent contract that accepts structured JSON and produces a unified Git patch.
- Patch preflight and application through `git apply`.
- Repository-native test command detection and subprocess execution with timeouts.
- Repair-agent contract for failed test runs.
- Deterministic security checks for risky Python execution patterns and likely hard-coded secrets.
- Verification engine combining quality/test commands with security findings.
- Risk-based human approval policy.
- Git workspace helpers and GitHub pull-request client.
- Persistent `ForgeRun` audit records.
- FastAPI endpoints for repository scanning and end-to-end forge runs.
- Optional workspace-root restriction for local-path API scanning.

## Important design rule

LLMs are not treated as the source of truth. Patch generation and semantic review are separated from deterministic test, security, Git, and verification layers.

## Quick start

```powershell
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest -q
python -m uvicorn redforge.main:app --app-dir backend --reload
```

Health endpoints:

- `GET /health`
- `GET /ready`

Repository intelligence:

- `POST /api/v1/repository/scan`

Forge workflow:

- `POST /api/v1/forge/runs`

By default, a Forge run performs repository understanding, planning, tests, verification, security evaluation, and approval evaluation. LLM patch generation is opt-in and requires an OpenAI-compatible provider configuration.

## LLM provider configuration

```env
REDFORGE_LLM_BASE_URL=http://localhost:11434/v1
REDFORGE_LLM_MODEL=qwen2.5-coder:7b
REDFORGE_LLM_API_KEY=
```

## Local path security

For API deployments, configure an allowed workspace root:

```env
REDFORGE_WORKSPACE_ROOT=C:\Users\saeed\Desktop
```

Paths outside this directory are rejected by the repository scan API.

## Status

`v1.0.0` establishes the first complete platform workflow and the interfaces required for future production hardening. External LLM quality, repository-specific build systems, branch protection, credential management, sandbox isolation, and GitHub permissions remain deployment concerns rather than assumptions made by the core platform.

## License

MIT
