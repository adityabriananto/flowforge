# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Introduced Semantic Versioning governance.
- Added Version Impact Assessment.
- Improved Release Strategy documentation.

## [1.0.0-beta] - 2026-07-12

### Added
- First public beta release of FlowForge (v1.0.0-beta).
- Implemented human-friendly PEP-440 compliant versioning across the CLI.
- Interactive CLI workflow for Mission Lifecycle management.
- Documentation for First Public Release.
- Engineering State consolidation (PROJECT_STATE.yaml as canonical state).

### Changed
- Removed deprecated ENGINEERING_STATE.yaml system and state synchronization fallbacks.
- Re-architected Runtime Orchestration to execute over the canonical Workspace.
- Refactored Provider APIs to gracefully accept arbitrary kwargs for contextual injections.
