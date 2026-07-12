# AI Contribution Guide

## Objective

All AI agents must adhere to the same rules to ensure consistent outcomes.

## Startup Checklist

- Read `README.md`
- Read `STATUS.md`
- Read `ROADMAP.md`
- Read all active sprint/mission documents.
- Do not begin coding if the mission scope does not explicitly authorize it.

## Product Core Phase Restrictions

FlowForge is currently in the **Product Core** phase.
During this phase:
- **No new engineering capabilities** may be introduced.
- **No architecture redesigns** are permitted.
- The sole focus is on Documentation, Packaging, Distribution, Quality, Testing, and Developer Experience.
- Respect the frozen nature of the Engineering Core. Do not modify the Runtime, Mission Planning Engine, or Mission Lifecycle.

## Roles

### Architect
- Designs the solution.
- Authors Architecture Decision Records (ADR).
- Does not implement code.

### Engineer
- Implements the tasks.
- Writes tests.
- Does not modify system architecture.

### Reviewer
- Reviews code quality.
- Reviews security.
- Reviews performance.

## Rules

- Do not add dependencies without approval.
- Do not modify the technology stack without approval.
- All architectural decisions must be documented as an ADR.
- All changes must strictly map to an active mission.
- Update relevant documentation upon task completion.

## Version Impact & Release Governance

Every completed FlowForge mission must be explicitly evaluated for its **Version Impact** during the engineering review before being closed.

### Version Impact Classification
Missions must be classified into one of the following impacts:
- **None**: No version change required.
- **Patch**: Bug fixes, documentation improvements, CLI improvements, internal refactoring without behavioural changes, packaging improvements.
- **Minor**: New capabilities, Planning Intelligence, Workspace Repair, new Mission Compiler features.
- **Major**: Breaking API changes, Mission Package incompatibility, Workspace format incompatibility.

### Engineering Workflow (Review Phase)
Before a mission is marked as complete, the reviewer must add the following assessment to the review document:
- **Version Impact**: (None / Patch / Minor / Major)
- **Reason**: Justification for the selected impact.
- **Recommended next version**: (Optional) e.g., `v1.0.1-beta`

## Backward Compatibility Policy

**Principle**: *The Engineering Workspace belongs to the project. FlowForge belongs to the toolchain.*

Whenever reasonably possible:
- Tool upgrades must not require Engineering Workspace recreation.
- Deprecated artifacts should be ignored gracefully.
- Workspace migration should remain optional.

## Branch Strategy

In accordance with the *Core Freeze Policy*, this repository adopts a long-term dual-branch strategy:

- **`main`**: Represents *stable FlowForge Core*. Only critical bug fixes, security patches, documentation improvements, and performance optimizations may be merged here. Experimental features are STRICTLY FORBIDDEN.
- **`next`**: Represents the future ecosystem of FlowForge. All new optional features (Dashboards, VS Code Extensions, Cloud Integrations, AI-assisted Planning, Marketplaces) are developed and validated exclusively on this branch.

## Tech Stack

Backend: Python + FastAPI
Frontend: React + TypeScript
Database: PostgreSQL
Queue: Redis
ORM: SQLAlchemy
