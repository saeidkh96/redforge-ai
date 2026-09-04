# RedForge AI

RedForge AI is an agentic software engineering platform designed to transform software issues into verified, human-approved pull requests.

## Target Workflow

Issue → Repository Understanding → Plan → Code → Test → Repair → Security / Regression Check → Human Approval → PR

## Core Principles

- LLMs are not the source of truth.
- Generation and verification are separate concerns.
- Deterministic verification is preferred whenever possible.
- Every execution should produce auditable evidence.
- Human approval remains part of high-impact software changes.

## Current Version

`v0.0.1`

Foundation release including:

- FastAPI application
- Configuration management
- Structured application logging
- Health and readiness endpoints
- Test foundation
- Ruff
- MyPy
- Docker
- GitHub Actions CI

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy