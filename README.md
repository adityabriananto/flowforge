# FlowForge

> **FlowForge is an Engineering Workflow Platform.**
> **It separates Planning, Execution, and Review while preserving Engineering Knowledge through the Engineering Workspace.**

FlowForge has been successfully validated through real-world engineering projects (including *BroDev Meeting Intelligence* and *BroDev Cashier*). The workflows and architecture documented here reflect the production workflow currently used by the FlowForge maintainers.

---

## What is FlowForge?

FlowForge is a standalone Python CLI tool that orchestrates the software engineering lifecycle. It does not replace developers or AI; rather, it manages the **Engineering Workspace**. Developers define goals and approve missions; AI providers execute the work; and FlowForge ensures the process is deterministic, isolated, and permanently recorded in your repository's Engineering Workspace.

## Why Use FlowForge?

- **Deterministic Workflows**: Stop relying on ad-hoc prompts. FlowForge enforces structured Mission Packages.
- **Provider Agnostic**: Switch between Gemini, OpenAI, or local CLI agents without changing your engineering processes.
- **Traceability**: Every mission, compilation, and execution is recorded. You always know *why* a change was made.
- **Human-in-the-Loop**: Execution requires your approval. FlowForge generates an Implementation Report before any code is finalized.

## How it Works

FlowForge operates on a simple lifecycle:
1. **Mission Creation**: You define what needs to be done.
2. **Compilation**: FlowForge gathers project context, constraints, and architecture rules to create a vendor-agnostic Mission Package.
3. **Execution**: An AI Provider reads the Mission Package and executes the task, producing an Implementation Report.
4. **Review**: You review the changes and mark the mission complete.

---

## Quick Start

The best way to learn FlowForge is to use it. Here's a complete lifecycle command reference:

```bash
# 1. Initialize the Engineering Workspace
flowforge init

# 2. Add an AI Provider (e.g., Google Gemini or OpenAI)
flowforge provider add

# View configured providers
flowforge providers

# 3. Create an Execution Profile
flowforge profile add

# View configured profiles
flowforge profiles

# 4. Author a new Mission using the Interactive Wizard
flowforge mission new

# 5. Compile the Mission into a Package
# Replace PROJECT-001 with your generated mission code
flowforge compile PROJECT-001

# 6. Execute the compiled package using a specific profile
flowforge run PROJECT-001 --profile executor
```

---

## Workspace Structure

When you run `flowforge init`, it creates an `.flowforge/` system directory and an `engineering/` documentation directory.

- **`.flowforge/`**: Internal system configuration, runtime logs, compiled packages, and profile setups.
- **`engineering/`**: Human-readable engineering documentation.
  - `active/`: Ongoing missions.
  - `completed/`: Finished missions.
  - `reports/`: AI-generated Implementation Reports.
  - `templates/`: Templates for reports and planning.

## Mission Flow

FlowForge follows a strict progression for completing tasks:

1. **Requirement**: A feature request or bug is identified.
2. **Mission**: A structured YAML definition of the goal and deliverables.
3. **Mission Package**: The compiled, context-rich package ready for AI execution.
4. **AI Executor**: The configured provider processes the package.
5. **Implementation Report**: The AI produces a detailed report of its work.
6. **Engineering Review**: A human reviews the code and the report before completion.

## Provider Overview

FlowForge is not a catalog of AI models. Instead, it uses a robust **Provider Architecture** where you configure *Providers* (the API or tool) and *Profiles* (the specific model and role).

Currently supported adapters:
- **Google Gemini API** (`google-genai` SDK)
- **OpenAI API** (Compatible with OpenAI, OpenRouter, Together AI)
- **Local Subprocess CLI** (Execute local shell scripts or local AI agents)

---

## Documentation

Before starting your first Engineering Workspace or contributing to FlowForge, we strongly encourage you to explore our documentation index for in-depth details:

- **[Concepts & Architecture](docs/concepts.md)**
- **[CLI Reference](docs/cli.md)**
- **[Engineering Workflow](docs/engineering-workflow.md)**
- **[System Architecture](docs/architecture.md)**

---

## Distribution Status

FlowForge is currently in **Public Beta**. It is distributed as a wheel package (`.whl`). PyPI distribution is planned for a future public release.

### Recommended (uv)
```bash
uv tool install path/to/flowforge-<version>.whl
```

### Standard Python (pip)
```bash
pip install path/to/flowforge-<version>.whl
```
