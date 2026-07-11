# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial preparation for public PyPI distribution.
- Added comprehensive Developer Onboarding, CLI Reference, and Concepts documentation.
- Dual-Identity model (`Engineering Identity` vs `System Identity`) to present a human-friendly `PROJECT-XXX` identity instead of UUIDs in the CLI.

### Changed
- The workspace architecture has been strictified into `engineering/` (long term engineering knowledge) and `.flowforge/` (transient execution and runtime state).
- The `flowforge compile` and `flowforge run` commands now exclusively reference the human-friendly Engineering Identity.

## [1.3.0] - 2026-06-15

### Added
- Introduced the **Mission Planning Engine**, deterministically generating structured `Mission` drafts from raw developer intents.
- Added `PlanningContextBuilder` to introspect repository states (`WORKSPACE.yaml` and `PROJECT_STATE.yaml`) and augment missions automatically.
- Integrated `MissionPackageCompiler` to bundle missions and their contexts into `.package.yaml` files for the runtime.
- Added `flowforge doctor` CLI command for environment diagnostics.

### Changed
- Shifted architecture from prompt-based execution to an orchestrated, deterministic Engineering Workflow.
- Finalized Clean Architecture boundaries for the internal Runtime and Services layers.
- Solidified the Provider layer abstractions to support OpenAI (Codex), Anthropic (Claude), and generic local providers without deep coupling.

## [1.0.0] - 2026-01-10

### Added
- Proof-of-Concept release for the Engineering Workspace paradigm.
- Initial interactive wizard for mission creation.
- Basic execution integration with OpenAI LLMs.
- File-based logging for engineering sessions.
