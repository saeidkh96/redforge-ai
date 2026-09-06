# RedForge AI Roadmap: v1.1.0 → v2.0.0

RedForge evolves as a verification-first agentic software engineering platform. Each milestone must preserve the core rule: **generation proposes; verification decides**.

## v1.1.0 — Automated Repair Loop

- Bounded Test → Repair → Retest loop.
- Configurable repair enablement and maximum attempts.
- Persisted repair-attempt evidence in `ForgeRun`.
- Minimal-scope repair-agent contract.

## v1.2.0 — Advanced Verification

- MyPy and coverage integration in the verification engine.
- Bandit/Semgrep adapters.
- Regression and changed-file-aware checks.
- Unified evidence model for deterministic gates.

## v1.3.0 — Sandboxed Execution

- Isolated patch/test execution boundary.
- Filesystem, process, CPU, memory, and timeout policies.
- Network access disabled by default with explicit allowlists.
- Disposable workspaces for untrusted changes.

## v1.4.0 — Runtime Identity & Permissions

- Agent/workload identity.
- Fine-grained tool permissions.
- Repository and data access policies.
- Explicit egress policy enforcement.

## v1.5.0 — Tamper-Resistant Audit Trail

- Append-only privileged-action events.
- Tool-call, patch, approval, and policy-decision traces.
- Hash-linked evidence records and exportable audit bundles.

## v1.6.0 — Reviewer Reliability

- Known-good and known-bad control sets.
- False-positive / false-negative tracking.
- Reviewer calibration and reliability scoring.
- Canary verification cases.

## v1.7.0 — Multi-Agent Verification

- Independent coding and review identities.
- Cross-agent verification.
- Reviewer disagreement handling.
- Deterministic arbitration rules for blocked changes.

## v1.8.0 — GitHub Workflow Automation

- Issue → branch → patch → checks → approval → PR workflow.
- Branch-protection-aware execution.
- PR evidence summaries and review metadata.
- Safe retry/idempotency for GitHub actions.

## v1.9.0 — Observability & Scale

- OpenTelemetry traces and metrics.
- Prometheus/Grafana integration.
- Job queue and concurrent ForgeRuns.
- Worker isolation and execution scheduling.

## v2.0.0 — Production-Grade Autonomous Engineering

- Controlled end-to-end autonomous workflow.
- Runtime identity, permissions, sandboxing, egress controls, and auditable privileged actions.
- Verification-backed autonomy boundaries.
- Production deployment and operational hardening.

### v2.0 operating boundary

**Identity → Permission → Action → Evidence → Verification → Approval → Audit**
