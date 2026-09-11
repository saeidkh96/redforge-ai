# RedForge AI v1.6.0 — Completed Implementation

The active package version is **1.6.0**.

v1.6.0 integrates the full autonomous engineering capability set into the working RedForge runtime rather than leaving later capabilities as roadmap-only placeholders.

## Implemented capability set

- Real GitHub Issue automation
  - signed GitHub webhook verification
  - delivery replay protection
  - label/action gating
  - authenticated issue retrieval
  - issue-to-run execution
  - opt-in audited PR delivery
- Deep repository intelligence
  - Python AST symbols and imports
  - Python call relationships
  - JavaScript/TypeScript imports
  - Java imports
  - C/C++ includes
  - direct/transitive impact estimation
  - changed/impacted symbol evidence
  - targeted test suggestions
- Agent intelligence and memory
  - specialized planner/coder/repair/reviewer/verifier roles
  - provider-independent LLM boundary
  - graph checkpoints and resume
  - SQLite engineering memory
  - prior-run recall
- Evaluation and reliability
  - benchmark observations
  - TP/TN/FP/FN tracking
  - precision, recall, accuracy, F1
  - persisted reliability history
- Production hardening
  - workspace boundary enforcement
  - secret redaction
  - evidence integrity hashing
  - fail-closed release gating
  - runtime policy and permissions
  - risk evaluation
  - deterministic review
  - human approval
  - tamper-evident audit
  - Docker execution evidence
  - controlled GitHub delivery

> Generation proposes. Verification decides.
