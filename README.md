# FlowForge

> **FlowForge is an Engineering Workflow Platform.**
> **It separates Planning, Execution, and Review while preserving Engineering Knowledge through the Engineering Workspace.**

FlowForge has been successfully validated through real-world engineering projects (including *BroDev Meeting Intelligence* and *BroDev Cashier*). The workflows and architecture documented here reflect the production workflow currently used by the FlowForge maintainers.

---

## What is FlowForge?

FlowForge is a standalone Python CLI tool that orchestrates the software engineering lifecycle. It does not replace developers or AI; rather, it manages the **Engineering Workspace**. Developers define goals and approve missions; AI providers execute the work; and FlowForge ensures the process is deterministic, isolated, and permanently recorded in your repository's Engineering Workspace.

---

## Distribution Status

FlowForge is currently in **Public Beta**.
During Public Beta, FlowForge is distributed as a wheel package (`.whl`). PyPI distribution is planned for a future public release.
The installation instructions below reflect the current Public Beta distribution model.

---

## Installation Guide

FlowForge can be installed globally as a standalone CLI tool.

### Recommended (uv)
If you use [uv](https://github.com/astral-sh/uv), you can install FlowForge as an isolated tool using the wheel package:
```bash
uv tool install path/to/flowforge-<version>.whl
```

### Standard Python (pip)
You can also install FlowForge via standard `pip`:
```bash
pip install path/to/flowforge-<version>.whl
```

---

## Future PyPI Installation

*Note: This installation method is **not yet available** during the current Public Beta.*

Once FlowForge is officially published to PyPI in a future stable release, installation will become:

**Using uv:**
```bash
uv tool install flowforge
```

**Using pip:**
```bash
pip install flowforge
```

---

## Verify Installation

Once installed, verify that FlowForge is available in your terminal:

```bash
flowforge --version
```
*Expected output: `FlowForge CLI Version: 1.0.0-beta` (or your installed version).*

You can also run the diagnostic tool to check your environment:
```bash
flowforge doctor
```
*Note: If you run this outside of an initialized project, it will inform you that no Engineering Workspace was detected. This is normal.*

---

## Your First Project

To start your first project and execute a complete Mission Lifecycle, run the following commands:

```bash
# 1. Create and enter a new directory
mkdir my-project
cd my-project

# 2. Initialize the Engineering Workspace
flowforge init

# 3. Author a new Mission
flowforge mission new

# 4. Start the Mission
flowforge mission start PROJECT-000

# 5. Compile the Mission into a Package
flowforge compile PROJECT-000

# 6. Execute the compiled package
flowforge run PROJECT-000

# 7. Complete the Mission
flowforge mission complete PROJECT-000
```

> **Note**: The commands above demonstrate the complete [Mission Lifecycle](docs/engineering-workflow.md#mission-lifecycle). In real engineering projects, implementations are typically reviewed before executing `flowforge mission complete`. For more details, see our recommended [Engineering Workflow](docs/engineering-workflow.md).

## Documentation

Before starting your first Engineering Workspace or contributing to FlowForge, we strongly encourage you to begin with the [Documentation Index](docs/README.md).

The documentation serves as your gateway to understanding the engineering philosophy, workflow, release process, and contributor guidelines in greater detail.

---

## Versioning Policy

FlowForge officially adopts [Semantic Versioning (SemVer 2.0.0)](https://semver.org/).
For detailed rules on release governance, version impact, and bump rules, please see our [Release Strategy](docs/release-strategy.md).

- **Current Release Channel**: Public Beta
- **Current Version**: `1.0.0-beta`

---

## Roadmap

FlowForge is currently in the **Product Core** phase, polishing the framework for the `v1.0.0-beta` release. See [ROADMAP.md](ROADMAP.md) for full details.
