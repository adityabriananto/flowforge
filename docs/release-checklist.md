# FlowForge Release Checklist

This document is the official release checklist used by FlowForge maintainers. It defines the standard operating procedure required to cut a new release and verify product readiness before publication.

## 1. Pre-Release Validation

### Product Metadata Verification
Verify that all public package metadata accurately represents the FlowForge package before publication.
- [ ] Product Name correctly defined (`flowforge`).
- [ ] Semantic Version correctly set across the repository.
- [ ] Authors and Maintainers explicitly listed.
- [ ] Homepage URL defined.
- [ ] Repository URL defined.
- [ ] Documentation URL defined (if available).
- [ ] Issue Tracker URL defined.
- [ ] Package Description accurately reflects current product positioning.
- [ ] Keywords updated (e.g., ai, agent, workflow, engineering, orchestration).
- [ ] License Metadata explicitly set (MIT).

### Developer Experience Validation
Verify that the first-time user experience is seamless. Focus strictly on usability and clarity.
- [ ] Installation requires no unexpected manual configuration.
- [ ] Quick Start documentation remains 100% accurate.
- [ ] README examples execute successfully without errors.
- [ ] CLI help pages (`flowforge --help` and subcommands) are clear and correct.
- [ ] Error messages are clear and provide actionable next steps.
- [ ] A first-time developer can reasonably reach their first completed mission within ~10 minutes.

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

## 2. Testing & Lifecycle Verification

### Testing
- [ ] Unit tests and integration tests passed (`uv run pytest tests/`).
- [ ] Fresh installation validated in a pristine directory.
- [ ] CLI command structure and `--version` output verified.

### Complete Mission Lifecycle Validation (Fresh Environment)
Verify the core workflow operates without repository-specific artifacts, explicitly covering every primary lifecycle command.
- [ ] `flowforge init`
- [ ] `flowforge mission new`
- [ ] `flowforge mission list`
- [ ] `flowforge mission show PROJECT-000`
- [ ] `flowforge compile PROJECT-000`
- [ ] `flowforge mission start PROJECT-000`
- [ ] `flowforge run PROJECT-000`
- [ ] `flowforge mission complete PROJECT-000`

## 3. Release Engineering

### Release Preparation
- [ ] Versions synchronized across the project (`pyproject.toml` and CLI strings).
- [ ] `CHANGELOG.md` updated with the new version and release notes.
- [ ] `ROADMAP.md` updated to reflect completed/current phases.
- [ ] Release Notes drafted and finalized.
- [ ] Commit changes: `git commit -m "chore(release): vX.Y.Z"`
- [ ] Annotated Git tag created: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Distribution artifacts generated (`uv build` produces `.whl` and `.tar.gz`).
- [ ] Push to remote: `git push origin main --tags`

### Publication
- [ ] **TestPyPI Publication (Optional)**: Publish and verify on TestPyPI to ensure metadata renders correctly.
- [ ] **PyPI Publication**: Publish the final package to PyPI (`uv publish`).
- [ ] **GitHub Release**: Create a GitHub Release mapping to the Git tag, including the final Release Notes.

### Post Release
- [ ] **Source Validation**: Verify the package installs successfully from the published source (`pip install flowforge` or `uv tool install flowforge`).
- [ ] **CLI Validation**: Verify CLI entry points work correctly on the published version.
- [ ] **Documentation**: Verify all documentation links remain valid on the public repository.
- [ ] **Announcement**: Release announcement checklist completed (e.g., community notifications).
- [ ] **Next Milestone**: The next development milestone/version is prepared in the tracking system.
