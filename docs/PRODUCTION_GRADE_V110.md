# RedForge AI v1.2.0 — Consolidated Production Platform

This release deliberately keeps the public package/release version at **1.2.0**
while consolidating the capability roadmap that had originally been split across
v1.2.0 through v2.0.0.

Implemented capability groups:

1. Automated Test → Repair → Retest loop
2. Advanced verification and regression gates
3. Policy-enforced command execution boundary
4. Runtime identity, permissions and workspace access checks
5. Explicit egress allow-list controls
6. Hash-chained tamper-evident audit records
7. Reviewer reliability / false-positive / false-negative metrics
8. Multi-agent verification consensus
9. Git/GitHub publication workflow primitive
10. Runtime metrics and concurrent job manager
11. Unified `ProductionRuntime` enforcement boundary

## Important execution boundary note

The portable sandbox layer enforces workspace, command, environment and timeout
policies before subprocess execution. For hostile/untrusted code, RedForge should
still be deployed inside an OS/container/VM isolation layer. Application-level
policy enforcement does not replace kernel-level isolation.

## Core principle

**Generation proposes. Verification decides.**
