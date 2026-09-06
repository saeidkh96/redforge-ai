<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

# RedForge AI

**Agentic Software Engineering Platform with verifiable autonomy, bounded repair, runtime policy enforcement, and auditable execution.**

> **Generation proposes. Verification decides.**

RedForge AI is designed around a controlled software-engineering workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Test → Repair → Advanced Verification → Runtime Policy → Human Approval → Audit → Pull Request**

## v1.2.0 — Full Roadmap Consolidation

RedForge AI v1.2.0 consolidates the capability roadmap that was previously planned across v1.2.0 through v2.0.0 into a single release while keeping the public package version at **1.2.0**.

The original milestone numbering remains documented in `docs/ROADMAP_V2.md` for traceability.

## Core Capabilities

### Repository Intelligence

- Repository file, language, manifest, framework, and project-type discovery
- Git-state inspection
- Dependency inventory
- Python symbol indexing
- Repository-aware target selection for planning
- Repository-native test command detection

### Planning and Code Generation

- Deterministic issue planning
- Provider-independent LLM gateway
- OpenAI-compatible provider adapter
- Deterministic provider for tests
- Structured coding-agent contract
- Unified Git patch generation
- Patch validation and application through `git apply`

### Test → Repair → Retest

- Bounded automated repair loop
- Configurable maximum repair attempts
- Repair only after failed repository-native tests
- Minimal repair-patch workflow
- Retesting after every repair attempt
- Persisted repair evidence in `ForgeRun`

### Advanced Verification

The verification layer can combine:

- Ruff
- MyPy
- pytest
- coverage
- regression-baseline checks
- deterministic security checks
- optional Bandit
- optional Semgrep

High- and critical-severity blocking findings can prevent a run from being accepted.

### Runtime Policy and Execution Controls

- Workspace-bound command execution
- Command allow-list
- Sanitized subprocess environment
- Execution timeout controls
- Runtime principals
- Explicit permissions
- Egress allow-list policy
- Sensitive-path approval rules
- Policy decisions: `ALLOW`, `DENY`, or `REQUIRE_APPROVAL`

The runtime model follows the boundary:

**Identity → Permission → Action → Evidence → Verification → Approval → Audit**

### Human Approval

Risk-sensitive operations can require explicit human approval before continuing, especially for sensitive repository paths and higher-impact actions.

### Tamper-Evident Audit

RedForge includes a SHA-256 hash-chained JSONL audit log with:

- sequence validation
- previous-hash validation
- event integrity checks
- tamper detection

### Reviewer Reliability

Reviewer quality can be tracked using:

- true positives
- true negatives
- false positives
- false negatives
- precision
- recall
- accuracy
- reliability scoring

### Multi-Agent Verification

Independent reviewer votes can be combined through configurable consensus logic using:

- approval counts
- rejection counts
- confidence-weighted approval
- configurable minimum approvals

### Git and GitHub Workflow

RedForge provides primitives for:

- branch creation
- repository status inspection
- committing changes
- GitHub pull-request creation

### Observability and Concurrency

- Thread-safe runtime metrics
- counters and duration tracking
- concurrent job execution
- job status and result handling

### Unified Production Runtime

`ProductionRuntime` brings together:

- principals and permissions
- runtime policy
- authorization
- sandboxed command execution
- advanced verification
- audit logging
- runtime evidence
- metrics

## Architecture

```text
Issue
  │
  ▼
Repository Intelligence
  │
  ▼
Planner Agent
  │
  ▼
Coding Agent
  │
  ▼
Patch Validation / Application
  │
  ▼
Test Orchestrator
  │
  ├── fail ──► Repair Agent ──► Retest
  │
  ▼
Advanced Verification
  │
  ▼
Runtime Policy / Risk Evaluation
  │
  ▼
Human Approval
  │
  ▼
Tamper-Evident Audit
  │
  ▼
Git / GitHub Workflow
  │
  ▼
Pull Request
```

The central execution record is `ForgeRun`, which captures the issue, repository context, plan, patches, test results, repair attempts, findings, verification results, approval state, and pull-request information.

## Quick Start

### 1. Create and activate a virtual environment

```powershell
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install RedForge AI

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Run quality gates

```powershell
python -m ruff format .
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python scripts\validate_v120_full.py
git diff --check
```

### 4. Start the API

```powershell
python -m uvicorn redforge.main:app --app-dir backend --reload
```

## API

Health:

- `GET /health`
- `GET /ready`

Repository intelligence:

- `POST /api/v1/repository/scan`

Forge workflow:

- `POST /api/v1/forge/runs`

## Configuration

### Automated Repair

```env
REDFORGE_REPAIR_ON_FAILURE=true
REDFORGE_MAX_REPAIR_ATTEMPTS=2
```

Example per-run overrides:

```json
{
  "generate_patch": true,
  "apply_patch": true,
  "repair_on_failure": true,
  "max_repair_attempts": 2
}
```

### LLM Provider

```env
REDFORGE_LLM_BASE_URL=http://localhost:11434/v1
REDFORGE_LLM_MODEL=qwen2.5-coder:7b
REDFORGE_LLM_API_KEY=
```

### Runtime / Verification

See `.env.example` for the current runtime settings, including production runtime, advanced verification, coverage threshold, allowed egress hosts, audit path, concurrency, and multi-agent approval configuration.

## Project Structure

```text
backend/redforge/
├── api/
├── core/
├── execution/
├── integrations/
├── models/
├── production/
│   ├── audit.py
│   ├── github_workflow.py
│   ├── jobs.py
│   ├── models.py
│   ├── multi_agent.py
│   ├── observability.py
│   ├── policy.py
│   ├── reliability.py
│   ├── runtime.py
│   └── sandbox.py
├── verification/
│   └── advanced.py
└── main.py

tests/
├── core/
├── execution/
└── production/

docs/
├── releases/
├── PRODUCTION_GRADE_V120.md
└── ROADMAP_V2.md

scripts/
└── validate_v120_full.py
```

## Validation Status

The v1.2.0 release has been locally validated with:

- Ruff
- pytest
- MyPy
- the v1.2.0 validation script

The local validation run completed with **30 passing tests**, no Ruff errors, and no MyPy issues across **54 source files**.

## Security and Isolation Note

RedForge's execution guard provides **application-level** workspace restrictions, command authorization, environment sanitization, timeout controls, permissions, and policy enforcement.

It is **not a kernel-level sandbox**.

Hostile or fully untrusted code should still execute inside a stronger isolation boundary such as a container, virtual machine, or equivalent operating-system sandbox.

## Roadmap Status

The capabilities originally planned across the v1.2.0 → v2.0.0 roadmap are consolidated into **v1.2.0**.

`docs/ROADMAP_V2.md` preserves the original milestone breakdown for architectural traceability.

## License

MIT
