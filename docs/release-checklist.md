# FlowForge Release Checklist

This document is the official release checklist used by FlowForge maintainers. It defines the standard operating procedure required to cut a new release and verify product readiness before publication.

## 1. Pre-Release Validation

### Installation Matrix
Maintainers must verify that FlowForge installs cleanly across the supported environments. Actual execution on every platform is not required during every patch release, but the matrix standardizes the verification target for major/minor releases.

| Platform | pip | uv tool |
|----------|-----|---------|
| Windows  | [OK] | [OK] |
| Linux    | [OK] | [OK] |
| macOS    | [OK] | [OK] |

### Backward Compatibility Validation
**Principle**: *FlowForge is stateless. Engineering projects are stateful.*
Verify that an existing Engineering Workspace created using a previous FlowForge version can continue operating seamlessly under the new version.

- [ ] Select an existing `engineering/` workspace project.
- [ ] Upgrade to the release candidate FlowForge version.
- [ ] `flowforge mission list` works and displays history intact.
- [ ] `flowforge compile` generates packages compatibly.
- [ ] `flowforge run` executes without migration errors.
- [ ] `flowforge mission complete` increments mission numbering and state correctly.

## 2. Release Checklist

### Repository
- [ ] `README.md` updated and aligns with current capabilities.
- [ ] `CHANGELOG.md` updated with the new version and release notes.
- [ ] `ROADMAP.md` updated to reflect completed/current phases.
- [ ] `LICENSE` verified.
- [ ] `CONTRIBUTING.md` verified.

### Packaging
- [ ] `pyproject.toml` version bumped and metadata verified.
- [ ] `uv build` successfully executed.
- [ ] Wheel (`.whl`) generated successfully in `dist/`.
- [ ] Source distribution (`.tar.gz`) generated successfully in `dist/`.

### Testing
- [ ] Unit tests and integration tests passed (`uv run pytest tests/`).
- [ ] Fresh installation validated in a pristine directory.
- [ ] CLI command structure and `--version` output verified.

### Engineering Workflow (Fresh Environment)
Verify the core workflow operates without repository-specific artifacts.
- [ ] `flowforge init`
- [ ] `flowforge mission new`
- [ ] `flowforge compile PROJECT-000`
- [ ] `flowforge run PROJECT-000`
- [ ] `flowforge mission complete PROJECT-000`

### Backward Compatibility
- [ ] Existing Engineering Workspace validated.
- [ ] Existing Mission Packages remain compatible.
- [ ] Existing Mission Lifecycle progresses correctly.

### Release & Publication
- [ ] Version numbers synchronized across the project (`pyproject.toml` and CLI strings).
- [ ] Release Notes finalized.
- [ ] Commit changes: `git commit -m "chore(release): vX.Y.Z"`
- [ ] Annotated Git tag created: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push to remote: `git push origin main --tags`
- [ ] Ready for PyPI publication (`uv publish`).
- [ ] GitHub Release created mapping to the Git tag.
