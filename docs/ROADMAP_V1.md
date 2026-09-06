# RedForge AI Roadmap to v1.0.0

| Version | Capability | v1 implementation |
| --- | --- | --- |
| v0.1.0 | Repository Understanding | scanner, Git metadata, dependencies, symbols |
| v0.2.0 | Issue → Plan | deterministic PlanningEngine |
| v0.3.0 | Plan → Code Patch | provider-independent CodingAgent + PatchEngine |
| v0.4.0 | Test + Repair | TestRunner + RepairAgent primitive |
| v0.5.0 | Verification + Security | VerificationEngine + SecurityScanner |
| v0.6.0 | Human Approval + PR | ApprovalEngine + GitHubClient |
| v0.7.0 | Reliability foundations | deterministic boundaries, audit models, safe defaults |
| v1.0.0 | End-to-End Workflow | ForgeOrchestrator + ForgeRun persistence + API |

Future releases should add sandboxed execution, richer code graphs, Semgrep/Bandit/CodeQL adapters, control/canary sets, reviewer calibration, multi-agent verification, protected Git workflows, and production observability.
