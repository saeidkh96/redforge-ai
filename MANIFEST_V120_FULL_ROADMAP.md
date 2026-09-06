# RedForge AI v1.2.0 Full Platform Manifest

Release version: **1.2.0**

This consolidated upgrade contains the complete roadmap capability set that was
previously described through v2.0.0, while intentionally retaining the v1.2.0
release identifier.

## New production modules

- `production/models.py`
- `production/policy.py`
- `production/audit.py`
- `production/sandbox.py`
- `production/reliability.py`
- `production/multi_agent.py`
- `production/github_workflow.py`
- `production/observability.py`
- `production/jobs.py`
- `production/runtime.py`
- `verification/advanced.py`

## Safety boundary

The execution layer is policy-enforced and portable. Real execution of hostile
code should additionally run inside container/VM/OS isolation.
