```{=html}
<p align="center">
```
`<img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">`{=html}
```{=html}
</p>
```
# RedForge AI

**Agentic Software Engineering Platform with verifiable autonomy,
bounded repair, runtime policy enforcement, human-gated delivery, and
auditable execution.**

> **Generation proposes. Verification decides.**

RedForge AI is designed around a controlled software-engineering
workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Patch → Test → Repair
→ Advanced Verification → Runtime Policy → Risk Evaluation →
Deterministic Review → Human Approval → Audit → GitHub Delivery**

## v1.3.0 --- End-to-End Production Integration

RedForge AI v1.3.0 connects the production-grade primitives introduced
in v1.2.0 directly to the `ForgeRun` lifecycle. The workflow now carries
policy decisions, risk assessment, deterministic review consensus, human
approval state, runtime evidence, audit events, and delivery state
through one orchestration path.

The capabilities originally planned across the v1.2.0 → v2.0.0 roadmap
remain consolidated in the project; v1.3.0 focuses on integrating those
capabilities into the end-to-end execution workflow.

## Core Capabilities

### Repository Intelligence

-   Repository file, language, manifest, framework, and project-type
    discovery
-   Git-state inspection
-   Dependency inventory
-   Python symbol indexing
-   Repository-aware target selection for planning
-   Repository-native test command detection

### Planning and Code Generation

-   Deterministic issue planning
-   Provider-independent LLM gateway
-   OpenAI-compatible provider adapter
-   Deterministic provider for tests
-   Structured coding-agent contract
-   Unified Git patch generation
-   Patch validation and application through `git apply`

### Test → Repair → Retest

-   Bounded automated repair loop
-   Configurable maximum repair attempts
-   Repair only after failed repository-native tests
-   Minimal repair-patch workflow
-   Retesting after every repair attempt
-   Persisted repair evidence in `ForgeRun`

### Advanced Verification

The verification layer can combine:

-   Ruff
-   MyPy
-   pytest
-   coverage
-   regression-baseline checks
-   deterministic security checks
-   optional Bandit
-   optional Semgrep

High- and critical-severity blocking findings can prevent a run from
being accepted.

### Runtime Policy and Execution Controls

-   Workspace-bound command execution
-   Command allow-list
-   Sanitized subprocess environment
-   Execution timeout controls
-   Runtime principals
-   Explicit permissions
-   Egress allow-list policy
-   Sensitive-path approval rules
-   Policy decisions: `ALLOW`, `DENY`, or `REQUIRE_APPROVAL`

The runtime model follows the boundary:

**Identity → Permission → Action → Evidence → Verification → Approval →
Audit**

### Human Approval

Risk-sensitive operations can require explicit human approval before
continuing, especially for sensitive repository paths and higher-impact
actions.

### Tamper-Evident Audit

RedForge includes a SHA-256 hash-chained JSONL audit log with:

-   sequence validation
-   previous-hash validation
-   event integrity checks
-   tamper detection

### Reviewer Reliability

Reviewer quality can be tracked using:

-   true positives
-   true negatives
-   false positives
-   false negatives
-   precision
-   recall
-   accuracy
-   reliability scoring

### Deterministic Multi-Reviewer Verification

Independent deterministic reviewer roles combine verification, security,
and risk/policy evidence through configurable consensus logic using:

-   approval counts
-   rejection counts
-   confidence-weighted approval
-   configurable minimum approvals
-   a hard verification/policy veto that cannot be outvoted by a simple
    majority

These reviewer roles are deterministic verification components; they are
not separate LLM agents.

### Git and GitHub Workflow

RedForge provides primitives for:

-   branch creation
-   repository status inspection
-   committing changes
-   remote branch push
-   GitHub pull-request creation
-   delivery authorization and audit evidence

### Observability and Concurrency

-   Thread-safe runtime metrics
-   counters and duration tracking
-   concurrent job execution
-   job status and result handling

### Unified Production Runtime

`ProductionRuntime` brings together:

-   principals and permissions
-   runtime policy
-   authorization
-   sandboxed command execution
-   advanced verification
-   audit logging
-   runtime evidence
-   metrics

## Architecture

``` text
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
Deterministic Review Consensus
  │
  ▼
Human Approval
  │
  ▼
Tamper-Evident Audit
  │
  ▼
Git / GitHub Delivery
  │
  ▼
Pull Request / Completed Run
```

The central execution record is `ForgeRun`, which captures the issue,
repository context, plan, patches, test results, repair attempts,
findings, verification results, policy decisions, risk assessment,
review consensus, pending approval actions, runtime evidence, delivery
readiness, approval state, and pull-request information.

## Quick Start

### 1. Create and activate a virtual environment

``` powershell
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install RedForge AI

``` powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Run quality gates

``` powershell
python -m ruff format .
python -m ruff check .
python -m pytest -q
python -m mypy backend\redforge
python scripts\validate_v130.py
git diff --check
```

### 4. Start the API

``` powershell
python -m uvicorn redforge.main:app --app-dir backend --reload
```

## API

Health:

-   `GET /health`
-   `GET /ready`

Repository intelligence:

-   `POST /api/v1/repository/scan`

Forge workflow:

-   `POST /api/v1/forge/runs`
-   `POST /api/v1/forge/runs/{run_id}/approve`
-   `POST /api/v1/forge/runs/{run_id}/reject`
-   `POST /api/v1/forge/runs/{run_id}/publish`

## Configuration

### Automated Repair

``` env
REDFORGE_REPAIR_ON_FAILURE=true
REDFORGE_MAX_REPAIR_ATTEMPTS=2
```

Example per-run overrides:

``` json
{
  "generate_patch": true,
  "apply_patch": true,
  "repair_on_failure": true,
  "max_repair_attempts": 2
}
```

### LLM Provider

``` env
REDFORGE_LLM_BASE_URL=http://localhost:11434/v1
REDFORGE_LLM_MODEL=qwen2.5-coder:7b
REDFORGE_LLM_API_KEY=
```

### Runtime / Verification

See `.env.example` for the current runtime settings, including
end-to-end integration, production runtime, advanced verification,
coverage threshold, allowed egress hosts, audit path, concurrency,
reviewer approval configuration, and the human-approval risk threshold.

For real GitHub delivery, the runtime egress allow-list must permit the
required GitHub hosts, such as `github.com` and `api.github.com`.

## Project Structure

``` text
backend/redforge/
├── api/
├── core/
├── execution/
├── integrations/
├── models/
├── production/
│   ├── audit.py
│   ├── github_workflow.py
│   ├── human_gate.py
│   ├── jobs.py
│   ├── models.py
│   ├── multi_agent.py
│   ├── observability.py
│   ├── policy.py
│   ├── reliability.py
│   ├── review.py
│   ├── risk.py
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
│   └── v1.3.0.md
├── PRODUCTION_GRADE_V120.md
└── ROADMAP_V2.md

scripts/
└── validate_v130.py
```

## Validation Status

The v1.3.0 release candidate has been locally validated with:

-   Ruff
-   pytest
-   MyPy
-   the v1.3.0 validation script
-   strict deterministic verification-veto smoke testing
-   sensitive-path policy-gate smoke testing
-   human-approval audit-chain validation

The local validation run completed with **34 passing tests**, no Ruff
errors, and no MyPy issues across **57 source files**. The v1.3
validator reported `ready: True`.

Bandit and Semgrep remain optional verification tools. The GitHub
delivery path is implemented with authorization, push, pull-request
creation, and audit hooks; real network delivery should be exercised
only with an explicitly configured repository, token, and egress
allow-list.

## Security and Isolation Note

RedForge's execution guard provides **application-level** workspace
restrictions, command authorization, environment sanitization, timeout
controls, permissions, and policy enforcement.

It is **not a kernel-level sandbox**.

Hostile or fully untrusted code should still execute inside a stronger
isolation boundary such as a container, virtual machine, or equivalent
operating-system sandbox.

## Roadmap Status

The capabilities originally planned across the v1.2.0 → v2.0.0 roadmap
were consolidated into **v1.2.0**. **v1.3.0** integrates those
production primitives into the main end-to-end `ForgeRun` workflow.

`docs/ROADMAP_V2.md` preserves the original milestone breakdown for
architectural traceability. Further work focuses on production
hardening, stronger isolation, deeper integration, and operational scale
rather than retroactively recreating the former milestone numbering.

## License

MIT
