<p align="center">
  <img src="docs/images/redforge_ai.png" alt="RedForge AI" width="420">
</p>

# RedForge AI

**Agentic Software Engineering Platform with autonomous runtime integration, deep repository intelligence, specialized agents, engineering memory, evaluation, production policy, human approval, and audited GitHub delivery.**

> **Generation proposes. Verification decides.**

RedForge AI is designed around a controlled software-engineering workflow rather than unconstrained code generation.

**Issue → Repository Understanding → Plan → Code → Patch → Test → Repair → Advanced Verification → Runtime Policy → Risk Evaluation → Deterministic Review → Human Approval → Audit → GitHub Delivery**

## v1.5.0 - Autonomous Runtime Integration
RedForge AI v1.5.0 is the first integration milestone after v1.4.0. It connects the existing ForgeRun production pipeline with the autonomous graph, checkpointing, deeper impact analysis, engineering memory, specialized agent roles, Docker execution, evaluation foundations, and controlled release gating.

### Roadmap delivered in this milestone

- **v1.5.0:** Autonomous Runtime Integration
- **v1.6.0:** GitHub Issue Automation foundations
- **v1.7.0:** Deep Repository Intelligence
- **v1.8.0:** Specialized Agent Intelligence + Engineering Memory
- **v1.9.0:** Evaluation and Reliability
- **v2.0.0:** Production Hardening and Release Gates

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

RedForge retains the `ForgeGraph` capability introduced earlier and v1.5.0 uses it as part of the integrated autonomy runtime:

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

The Docker execution layer introduced earlier remains part of the v1.5.0 runtime boundary with configurable controls such as:

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

The provider-independent LLM routing layer remains available for:

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

v1.5.0 adds `IntegratedAutonomyRuntime`, which connects the graph/checkpoint layer to the established `ForgeOrchestrator`, deep impact analysis, Docker execution evidence, release gating, and persistent engineering memory.

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

v1.5.0 integrates the `roadmap_v200` capability layer around the established v1.4 foundation, including deep multi-language impact analysis, specialized agents, GitHub issue intake, benchmark evaluation, release gating, and an integrated autonomy runtime.

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
python scripts\validate_v150.py
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

v1.5.0 registers the autonomy router in `redforge.main` and adds deep impact analysis plus authenticated GitHub issue retrieval alongside the existing autonomy endpoints.

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
├── roadmap_v200/
│   ├── agents.py
│   ├── evaluation.py
│   ├── github_live.py
│   ├── hardening.py
│   ├── intelligence.py
│   ├── models.py
│   ├── runtime.py
│   └── service.py
├── verification/
└── main.py

tests/
├── production/
├── roadmap_v140/
└── roadmap_v200/

docs/
├── ROADMAP_V140_CONSOLIDATED.md
├── ROADMAP_V150_TO_V200.md
└── releases/
    └── v2.0.0.md

scripts/
└── validate_v200.py
```

## Validation Status

The v2.0.0 bundle was compatibility-tested in a reconstructed RedForge workspace using the available v1.x release overlays. The targeted v2 suite completed with **12 passing tests**, and `scripts/validate_v200.py` reported `ready: True`. Python compilation also passed for the bundle.

Because the active repository on your machine is the source of truth, run the complete project gates after copying this overlay before committing or tagging v1.5.0:

```powershell
python -m pip install -e ".[dev]"
python -m ruff format .
python -m ruff check .
python -m mypy backend\redforge
python -m pytest -q
python scripts\validate_v150.py
git diff --check
```

Do not create the v1.5.0 tag until all of those gates pass in the real repository.

## Security and Isolation Note

RedForge has two relevant execution-control layers:

1. The production runtime provides application-level workspace restrictions, command authorization, environment sanitization, timeout controls, permissions, and policy enforcement.
2. The Docker-based isolation layer remains available and is surfaced as runtime evidence in the v2 integration layer.

Docker isolation improves the execution boundary, but the current implementation should not be presented as a complete hostile-code or kernel-level security sandbox.

Fully untrusted workloads require additional production hardening and an appropriately secured container, virtual-machine, or operating-system isolation strategy.

## Roadmap Status

v1.5.0 begins the post-v1.4 integration roadmap. The codebase already contains foundations for several later roadmap capabilities, while future releases will focus on deeper integration, real-world automation, reliability evaluation, and production hardening.

Live GitHub delivery still requires explicit credentials and egress authorization. Docker improves isolation but is not a claim of perfect hostile-code containment.

## License

MIT
