<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

<h1 align="center">RedForge AI</h1>

<p align="center">
  <strong>Verifiable Agentic Software Engineering</strong><br>
  Repository intelligence, planning, code generation, testing, repair, verification, risk evaluation, and human approval in one auditable workflow.
</p>

<p align="center">
  <code>v1.0.0</code> · <code>Python 3.14+</code> · <code>FastAPI</code> · <code>MIT</code>
</p>

---

## Overview

RedForge AI is an agentic software engineering platform built around a simple principle:

> **LLMs can propose changes. Evidence decides whether those changes are acceptable.**

Instead of treating code generation as the end of the workflow, RedForge surrounds generation with repository understanding, deterministic checks, security analysis, risk evaluation, and human approval.

```text
Issue
  ↓
Repository Understanding
  ↓
Plan
  ↓
Code / Patch
  ↓
Test
  ↓
Repair
  ↓
Security + Regression Verification
  ↓
Risk Evaluation
  ↓
Human Approval when required
  ↓
Pull Request
```

The core execution unit is a **ForgeRun**: an auditable record connecting the issue, repository snapshot, plan, patch, tests, verification results, approval decision, and pull-request state.

## Why RedForge AI?

Many coding-agent workflows optimize for producing a plausible patch. RedForge is designed around producing a patch that can be **understood, checked, rejected, repaired, and audited**.

Its architecture keeps generation separate from verification:

- the **Coding Agent** proposes changes;
- deterministic tooling validates repository and test behavior;
- the **Security Scanner** looks for defined risky patterns;
- the **Verification Engine** aggregates evidence;
- the **Approval Engine** evaluates risk and determines whether human review is required;
- Git and GitHub integrations provide the path toward a controlled pull request.

This separation prevents an LLM from becoming its own source of truth.

## v1.0.0 capabilities

### Repository Intelligence

RedForge builds a deterministic repository snapshot containing:

- files and repository size;
- language distribution;
- manifests and configuration files;
- framework and project-type detection;
- test files and likely entry points;
- Git branch, HEAD, dirty state, remotes, and recent commits;
- dependency inventory;
- Python AST symbol indexing for functions and classes.

### Planning

The planning engine converts an issue and repository context into structured implementation steps with likely target files and risk notes. The current planner is deterministic, keeping the initial decision path reproducible.

### Provider-independent Agent Layer

The LLM layer is intentionally decoupled from the core platform. v1.0.0 includes:

- an LLM provider protocol;
- an OpenAI-compatible provider adapter;
- a deterministic static provider for tests;
- a Coding Agent that expects structured output and produces unified Git patches;
- a separate semantic Reviewer Agent contract;
- a Repair Agent primitive for failed test scenarios.

The core platform does not require a specific hosted LLM vendor.

### Patch Execution

Generated patches are checked before modification and applied using Git-native semantics:

```text
git apply --whitespace=error --check
git apply --whitespace=error
```

This provides a deterministic preflight before a patch touches the working tree.

### Test Orchestration

RedForge detects repository-native test commands for supported project types and executes them with captured output, return codes, durations, and timeouts.

Current command detection includes:

| Ecosystem | Command |
| --- | --- |
| Python | `python -m pytest -q` |
| Node.js | `npm test -- --runInBand` |
| Rust | `cargo test --quiet` |
| Go | `go test ./...` |

Python subprocesses use the active RedForge interpreter, allowing virtual-environment tooling to remain consistent during ForgeRun verification.

### Verification and Security

The Verification Engine combines deterministic quality/test execution with security findings. The current Python verification path includes Ruff and pytest.

The built-in security scanner detects selected high-risk patterns including:

- Python `eval()` and `exec()` usage;
- selected subprocess calls using `shell=True`;
- likely hard-coded secrets in supported text/source files.

The built-in scanner is deliberately lightweight. It is an architectural verification layer, not a replacement for tools such as Semgrep, Bandit, CodeQL, or enterprise security review.

### Risk-based Human Approval

Verification and risk are separate decisions. RedForge can require human approval when a change is sensitive, broad, or fails verification.

Risk evaluation considers signals such as:

- verification failure;
- high/critical findings;
- sensitive paths;
- unusually broad patches.

Low-risk, verified runs can proceed without mandatory approval, while higher-impact changes remain gated.

### Persistence and Auditability

ForgeRun state can be persisted under `.redforge/runs/`, providing an execution record for local workflows. Runtime state is intended to remain outside version control.

### Git and GitHub Integration

v1.0.0 provides primitives for:

- branch creation;
- repository status inspection;
- commits;
- GitHub pull-request creation through the GitHub REST API.

Pull-request creation requires caller-provided GitHub credentials and is not automatically triggered by every ForgeRun.

## Architecture

```text
┌───────────────────────────┐
│           Issue           │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Repository Intelligence  │
│ files · Git · deps · AST  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Planning Engine      │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Coding Agent        │
│ provider-independent LLM  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Patch Engine        │
│ git apply check / apply   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Test Runner / Repair Agent│
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    Verification Engine    │
│ tests · quality · security│
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Risk + Human Approval    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        Git / GitHub       │
│       Pull Request        │
└───────────────────────────┘
```

## Project structure

```text
redforge-ai/
├── backend/redforge/
│   ├── agents/          # LLM gateway, coding, review
│   ├── api/             # FastAPI routes
│   ├── approval/        # Risk and approval policy
│   ├── core/            # Configuration and Forge orchestrator
│   ├── execution/       # Patch, test, and repair execution
│   ├── integrations/    # Git and GitHub integrations
│   ├── models/          # ForgeRun domain models
│   ├── persistence/     # Local run persistence
│   ├── planning/        # Issue-to-plan engine
│   ├── repository/      # Repository intelligence
│   ├── security/        # Deterministic security checks
│   └── verification/    # Verification engine
├── docs/
├── infra/
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Quick start

### Requirements

- Python 3.14+
- Git

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/saeidkh96/redforge-ai.git
cd redforge-ai
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the local quality gates:

```powershell
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python scripts\validate_v100.py
```

Start the API:

```powershell
python -m uvicorn redforge.main:app --reload
```

## API

### Health

```http
GET /health
GET /ready
```

### Repository scan

```http
POST /api/v1/repository/scan
```

Example body:

```json
{
  "path": "C:\\path\\to\\repository"
}
```

The response includes repository metadata, detected languages, project types, frameworks, dependencies, symbols, test files, entry points, and Git state.

### ForgeRun

```http
POST /api/v1/forge/runs
```

Example without LLM patch generation:

```json
{
  "repository_path": "C:\\path\\to\\repository",
  "issue": {
    "title": "Improve repository validation",
    "body": "Add deterministic validation for the requested behavior."
  },
  "generate_patch": false,
  "apply_patch": false
}
```

A default non-generating ForgeRun performs repository understanding, planning, tests, verification, security evaluation, risk evaluation, and approval evaluation.

Patch generation is opt-in.

## LLM provider configuration

RedForge can communicate with an OpenAI-compatible endpoint without coupling the core platform to one model vendor.

```env
REDFORGE_LLM_BASE_URL=http://localhost:11434/v1
REDFORGE_LLM_MODEL=qwen2.5-coder:7b
REDFORGE_LLM_API_KEY=
```

Model quality and structured-output reliability depend on the selected provider/model.

## Workspace security

For API deployments, restrict repository access to an allowed workspace root:

```env
REDFORGE_WORKSPACE_ROOT=C:\Users\saeed\Desktop
```

Repository-scan requests outside the configured workspace are rejected.

For stronger isolation, RedForge should ultimately execute untrusted repository workloads inside disposable sandboxes or containers rather than directly on the host. That isolation layer is not part of v1.0.0.

## v1.0.0 validation

The v1.0.0 release candidate was locally validated with:

```text
Ruff                         PASS
Pytest                       PASS — 22 tests
MyPy                         PASS — 42 source files
v1.0.0 validation script     PASS
Health / readiness API       PASS
Repository scan smoke test   PASS
ForgeRun verification        PASS
Security findings            0 in smoke validation
ForgeRun risk                LOW
```

The ForgeRun smoke validation executed Ruff and pytest through the active project virtual environment and produced `verification.passed = true`.

## Current limitations

v1.0.0 establishes the complete architectural workflow, but it should not be interpreted as unrestricted autonomous production execution.

Current limitations include:

- repair exists as an agent primitive but is not yet a fully autonomous bounded repair loop in the default orchestrator;
- semantic LLM review exists as a separate primitive but is not yet a mandatory stage in every verification run;
- the built-in security scanner covers a focused deterministic rule set rather than full SAST coverage;
- GitHub PR creation requires credentials and explicit integration usage;
- repository-specific build systems may require custom commands;
- untrusted code is not yet executed inside a disposable runtime sandbox;
- production credential management, branch protection, policy enforcement, and deployment isolation remain external concerns.

These boundaries are intentional: RedForge favors explicit guarantees over claiming autonomy that the platform cannot yet verify.

## Roadmap beyond v1.0.0

The next stage focuses on production hardening and verification depth rather than simply adding more generation capability:

- bounded automatic test → repair → retest loops;
- mandatory semantic review policies where appropriate;
- Semgrep/Bandit/CodeQL-style security adapters;
- static typing and repository-specific quality-gate profiles;
- disposable sandbox/container execution;
- richer dependency and impact analysis;
- control/canary test sets for verification calibration;
- reviewer false-positive/false-negative tracking;
- cross-agent verification and reviewer reliability scoring;
- stronger GitHub policy and branch-protection integration;
- observability for long-running ForgeRuns;
- additional LLM provider adapters while keeping the core vendor-independent.

See `docs/ROADMAP_V1.md` for the v1 milestone history and project direction.

## Design principles

1. **LLM ≠ source of truth** — generated output must be independently verifiable.
2. **Generation ≠ verification** — agents that propose changes should not be the only judges of those changes.
3. **Deterministic evidence first** — tests, static checks, Git state, and security rules should carry explicit evidence.
4. **Minimal safe patches** — prefer constrained, reviewable changes over broad rewrites.
5. **Human control for impact** — high-risk changes require explicit approval.
6. **Auditability** — important decisions and execution results belong to the ForgeRun record.
7. **Vendor independence** — model providers are adapters, not the architecture.

## Contributing

Contributions, issues, and technical discussions are welcome. Before submitting a change, run:

```powershell
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
```

Changes to verification, security, approval, or execution behavior should include focused tests and preserve the separation between generation and deterministic verification.

## License

RedForge AI is released under the **MIT License**. See `LICENSE` for details.
