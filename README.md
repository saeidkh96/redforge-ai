<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

# RedForge AI

**Agentic Software Engineering Platform with verifiable autonomy, bounded repair, runtime policy enforcement, human-gated delivery, auditable execution, graph-based orchestration, and engineering memory.**

> **Generation proposes. Verification decides.**

RedForge AI is designed around a controlled software-engineering workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Patch → Test → Repair → Advanced Verification → Runtime Policy → Risk Evaluation → Deterministic Review → Human Approval → Audit → GitHub Delivery**

## v1.4.0 — Autonomous Engineering Roadmap Consolidation

RedForge AI v1.4.0 extends the existing end-to-end production workflow with a new autonomous-engineering capability layer.

This release adds foundations for graph-based orchestration, checkpoint and resume, Docker-based isolated execution, repository impact analysis, multi-provider LLM routing, persistent engineering memory, GitHub issue autonomy planning, and a unified autonomous-engineering platform facade.

The focus of v1.4.0 is capability consolidation while keeping generation, verification, policy, approval, and delivery responsibilities clearly separated.

## Core Capabilities

### Repository Intelligence

- Repository file, language, manifest, framework, and project-type discovery
- Git-state inspection
- Dependency inventory
- Python symbol indexing
- Repository-aware target selection for planning
- Repository-native test command detection
- Python import/dependency impact analysis for changed files

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

### Graph-Based Orchestration

The v1.4.0 capability layer introduces `ForgeGraph` for autonomous workflow orchestration with:

- named workflow nodes
- conditional transitions
- bounded execution steps
- checkpoint persistence
- resume support
- execution state tracking

This provides a foundation for longer-running engineering workflows without making the LLM the source of truth.

### Checkpoint and Resume

`CheckpointStore` persists workflow state so an autonomous run can continue from a known checkpoint instead of restarting the complete workflow.

### Docker-Based Isolated Execution

v1.4.0 adds a Docker execution layer with configurable controls such as:

- isolated container execution
- network disabled by default
- CPU and memory limits
- read-only container mode
- temporary writable filesystem
- execution timeout
- dry-run command generation

This is a stronger isolation option than application-level subprocess restrictions, but it should not be treated as a complete hostile-code security boundary without additional production hardening.

### Repository Impact Analysis

The Python impact analyzer uses AST-based import analysis to build repository relationships and estimate which Python modules may be affected by a change.

It is intentionally focused on Python import-level analysis and is not yet a full cross-language semantic call graph.

### LLM Routing and Fallback

The v1.4.0 LLM router provides foundations for:

- multiple model/provider candidates
- provider priority
- fallback behavior
- provider failure budgets
- usage evidence
- cost-guard configuration

The core remains provider-independent.

### Engineering Memory

RedForge now includes SQLite-backed engineering memory for persistent workflow knowledge and evidence.

The memory layer supports storing and retrieving structured engineering records while keeping persistence separate from agent reasoning.

### GitHub Autonomy Planning

`GitHubAutonomyPlanner` provides structured planning for GitHub-driven autonomous work, including repository/workspace context, branch planning, and issue-derived execution envelopes.

Live GitHub automation still depends on explicit credentials, network access, repository configuration, and runtime authorization.

### Autonomous Engineering Platform

`AutonomousEngineeringPlatform` provides a unified stage-oriented facade around the autonomous workflow:

**Understand → Plan → Code → Patch → Test → Repair → Verify → Policy → Risk → Review → Approval → Audit → Delivery**

The v1.4.0 implementation provides the orchestration foundation and callback-based stage integration. Deeper production integration remains an ongoing engineering task.

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

### Deterministic Multi-Reviewer Verification

Independent deterministic reviewer roles combine verification, security, and risk/policy evidence through configurable consensus logic using:

- approval counts
- rejection counts
- confidence-weighted approval
- configurable minimum approvals
- a hard verification/policy veto that cannot be outvoted by a simple majority

These reviewer roles are deterministic verification components; they are not separate LLM agents.

### Git and GitHub Workflow

RedForge provides primitives for:

- branch creation
- repository status inspection
- committing changes
- remote branch push
- GitHub pull-request creation
- delivery authorization and audit evidence

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
Planner / Autonomous Graph
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

The central v1.3 execution record remains `ForgeRun`, which captures the issue, repository context, plan, patches, test results, repair attempts, findings, verification results, policy decisions, risk assessment, review consensus, pending approval actions, runtime evidence, delivery readiness, approval state, and pull-request information.

v1.4.0 adds the `roadmap_v140` autonomous capability layer around this foundation, including graph orchestration, checkpointing, Docker execution, impact analysis, LLM routing, engineering memory, and autonomy planning.

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
python scripts\validate_v140.py
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
- `POST /api/v1/forge/runs/{run_id}/approve`
- `POST /api/v1/forge/runs/{run_id}/reject`
- `POST /api/v1/forge/runs/{run_id}/publish`

v1.4.0 also includes autonomy API implementation for repository impact analysis and GitHub issue execution-envelope generation. Router registration should be verified in the deployed application configuration before treating these routes as externally available.

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

See `.env.example` for the current runtime settings, including end-to-end integration, production runtime, advanced verification, coverage threshold, allowed egress hosts, audit path, concurrency, reviewer approval configuration, and the human-approval risk threshold.

For real GitHub delivery, the runtime egress allow-list must permit the required GitHub hosts, such as `github.com` and `api.github.com`.

## Project Structure

```text
backend/redforge/
├── api/
│   └── autonomy.py
├── core/
├── execution/
├── integrations/
├── models/
├── production/
├── roadmap_v140/
│   ├── autonomy.py
│   ├── checkpoint.py
│   ├── graph.py
│   ├── intelligence.py
│   ├── llm_router.py
│   ├── memory.py
│   ├── models.py
│   ├── platform.py
│   └── sandbox.py
├── verification/
│   └── advanced.py
└── main.py

tests/
├── core/
├── execution/
├── production/
└── roadmap_v140/

docs/
├── releases/
│   ├── v1.3.0.md
│   └── v1.4.0.md
├── ROADMAP_V140_CONSOLIDATED.md
├── PRODUCTION_GRADE_V120.md
└── ROADMAP_V2.md

scripts/
├── validate_v130.py
└── validate_v140.py
```

## Validation Status

The v1.4.0 release was locally validated with:

- Ruff
- pytest
- MyPy
- the v1.4.0 validation script
- Git whitespace validation

The final local validation completed with:

- **40 passing tests**
- **Ruff: PASS**
- **MyPy: PASS across 68 source files**
- **v1.4.0 validator: `ready: True`**
- **`git diff --check`: PASS**

The v1.4.0 validator confirmed the presence of graph orchestration, checkpointing, Docker sandbox command generation, impact analysis, engineering memory, and LLM routing.

Bandit and Semgrep remain optional verification tools. Real GitHub delivery and autonomous external actions should be exercised only with explicitly configured repositories, credentials, runtime permissions, and network allow-lists.

## Security and Isolation Note

RedForge has two relevant execution-control layers:

1. The production runtime provides application-level workspace restrictions, command authorization, environment sanitization, timeout controls, permissions, and policy enforcement.
2. v1.4.0 adds Docker-based isolated execution with configurable network and resource controls.

Docker isolation improves the execution boundary, but the current implementation should not be presented as a complete hostile-code or kernel-level security sandbox.

Fully untrusted workloads require additional production hardening and an appropriately secured container, virtual-machine, or operating-system isolation strategy.

## Roadmap Status

v1.4.0 consolidates RedForge's planned autonomous-engineering capability layer into one milestone.

The project now has foundations for graph orchestration, checkpoint/resume, isolated execution, deeper repository analysis, provider-independent LLM routing, engineering memory, GitHub autonomy planning, and autonomous engineering workflows.

Further work focuses on deeper end-to-end integration, production hardening, live GitHub automation, stronger hostile-code isolation, richer cross-language repository intelligence, and real-world autonomous workflow evaluation.

## Release

- Version: **v1.4.0**
- Merge commit: `b0b5de40ef442266205dcaa951842eaa40a51248`
- Release theme: **Autonomous Engineering Roadmap Consolidation**

## License

MIT
