# FlowForge Release Strategy

This document outlines the official strategy and flow for cutting and distributing new public versions of FlowForge.

## The Standard Release Flow

The release of a new FlowForge version follows a strictly sequential, standardized pipeline:

```text
Development (main branch)
       ↓
Version Update (pyproject.toml, CLI internals)
       ↓
Automated Tests & Local Validation
       ↓
Package Build (uv build)
       ↓
Release Checklist Verification (docs/release-checklist.md)
       ↓
Annotated Git Tag (vX.Y.Z)
       ↓
GitHub Release (Draft -> Published)
       ↓
PyPI Publication (uv publish)
       ↓
Developer Installation (pip install / uv tool install)
```

## Internal vs Public Versioning
- **Internal Engineering History**: During the initial Dogfooding phases (Engineering Core and Product Core), FlowForge utilized internal version numbers (e.g., `1.1.x`, `1.2.x`, `1.3.x`). These strictly represent internal milestones and are not publicly documented outside of the Git history.
- **Public Releases**: The public product lifecycle begins officially with `v1.0.0-beta`. From this point forward, FlowForge strictly adheres to [Semantic Versioning](https://semver.org/).

## Tagging & Branching
- **Main Branch**: `main` serves as the primary source of truth. All releases are tagged directly on `main` when they pass the Release Checklist.
- **Tags**: Use annotated tags mapping to the semantic version with a `v` prefix. (e.g., `git tag -a v1.0.0-beta -m "Release v1.0.0-beta"`).

## Verification Principles
Before a tag is pushed, the release MUST be validated against the `release-checklist.md`, particularly confirming that:
- Backward compatibility is preserved (no forced migrations for existing `engineering/` workspaces).
- The package successfully installs in a pristine environment.
- The End-to-End Mission Lifecycle works without requiring specialized repository knowledge.
