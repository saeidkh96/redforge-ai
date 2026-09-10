# RedForge AI - v1.5.0 to v2.0.0 Roadmap
This roadmap defines the staged development path from v1.5.0 through v2.0.0. Some capability foundations may be introduced earlier, while each release focuses on deeper integration, validation, and production maturity.

## v1.5.0 - Autonomous Runtime Integration

- `IntegratedAutonomyRuntime` connects the established `ForgeOrchestrator` production pipeline to engineering memory, deeper impact analysis, and fail-closed release gating.

## v1.6.0 - Real GitHub Issue Automation

- authenticated GitHub issue retrieval
- issue-to-execution envelope planning
- existing audited GitHub branch/commit/push/PR workflow remains the delivery mechanism

## v1.7.0 - Deep Repository Intelligence

- Python AST imports and symbols
- JavaScript/TypeScript import discovery
- Java import discovery
- C/C++ include discovery
- direct/transitive impact estimation
- test targeting hints

## v1.8.0 - Agent Intelligence and Memory

- specialized planner/coder/repair/reviewer/verifier roles
- provider-independent agent interface
- persistent engineering-run memory through the established SQLite memory layer

## v1.9.0 - Evaluation and Reliability

- benchmark cases
- deterministic observations
- aggregate success-rate metrics
- known-good / known-bad workflow evaluation foundation

## v2.0.0 - Production Hardening

- fail-closed release gate
- workspace boundary enforcement
- secret redaction
- production runtime evidence integration
- Docker isolation foundation from v1.4
- human approval remains mandatory when policy/risk requires it

## Important boundary

v2.0.0 is a production-oriented engineering milestone, not a claim that arbitrary hostile code is perfectly isolated or that live GitHub actions can run without credentials and explicit network authorization.
