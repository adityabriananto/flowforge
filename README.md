# FlowForge

> **Engineering projects accumulate knowledge over time.**
> **Traditional AI conversations lose engineering context.**
> **FlowForge preserves engineering knowledge inside an Engineering Workspace.**
>
> **FlowForge plans engineering.**
> **Providers execute engineering.**
> **Developers approve engineering decisions.**

---

## 1. Introduction

FlowForge is an **Engineering Operating System (EOS)** designed to orchestrate the entire software engineering lifecycle in collaboration with Artificial Intelligence (AI). 

Unlike chat-based AI coding assistants, FlowForge shifts the source of truth from transient conversation histories to a persistent, repository-owned Engineering Workspace. FlowForge treats LLMs as interchangeable *execution providers*, ensuring your project's architecture, memory, and history remain local and independent of any single AI vendor.

## 2. Philosophy

FlowForge exists because software engineering requires long-term context.

Traditional AI chat interfaces are excellent at solving isolated problems but fail to retain architectural decisions across long-term development cycles. FlowForge solves this by introducing a strict **Engineering Workflow** where AI agents read from and write to a standardized project state, allowing an agent to safely resume where another left off weeks or months later.

## 3. Key Concepts

- **Engineering Workspace**: The persistent repository state where knowledge accumulates.
- **Mission**: A declarative unit of engineering work that flows from backlog to completion.
- **Mission Package**: A compiled, vendor-agnostic bundle of instructions ready for AI execution.
- **Runtime**: The stateless coordinator orchestrating the end-to-end execution.
- **Provider**: The abstraction layer representing the AI execution driver (e.g., Claude, Ollama).

For a complete glossary, refer to the [Concepts & Terminology Guide](docs/concepts.md).

## 4. Installation

FlowForge requires **`uv`** for modern Python package management.

```bash
# 1. Install FlowForge globally via uv
uv tool install flowforge

# (Alternatively, you can clone the repository and run via uv sync)
```

## 5. Quick Start

Create and execute your first mission in minutes:

```bash
# 1. Initialize the Engineering Workspace in your project
flowforge init
# What happens: Creates the .flowforge and engineering directories.
# Why it exists: Establishes the repository's long-term memory.
# Artifact: PROJECT_STATE.yaml, WORKSPACE.yaml

# 2. Start the Interactive Mission Authoring Wizard
flowforge mission new
# What happens: Guides you to define a title and business goal.
# Why it exists: Converts human intent into an engineering backlog item.
# Artifact: A drafted mission YAML in engineering/missions/backlog/

# 3. Compile the Mission
flowforge compile PROJECT-000
# What happens: Merges the mission with workspace context into a package.
# Why it exists: Translates raw goals into AI-actionable constraints.
# Artifact: A Mission Package ready for execution.

# 4. Mark the Mission as Active
flowforge mission start PROJECT-000
# What happens: Moves the mission to the active directory.
# Why it exists: Signals that the project is currently working on this task.

# 5. Execute the Mission
flowforge run PROJECT-000
# What happens: Invokes the AI Provider to execute the Mission Package.
# Why it exists: Automates the actual software engineering implementation.
# Artifact: Code changes and an immutable Engineering Session log.

# 6. Complete the Mission
flowforge mission complete PROJECT-000
# What happens: Finalizes the task and updates project state.
# Why it exists: Permanently records the outcome in the long-term memory.
# Artifact: Updated PROJECT_STATE.yaml
```

## 6. Engineering Workflow

The FlowForge workflow separates **Planning** (what needs to be done) from **Execution** (how the AI writes the code). Developers define the goal and approve the plan, while FlowForge orchestrates the state transitions and delegates execution to interchangeable AI Providers.

Read the detailed [Developer Onboarding Guide](docs/onboarding.md) to understand the workflow in depth.

## 7. Architecture Overview

FlowForge strictly separates the execution environment from the planning environment:

```text
    Developer
        ↓
  Mission Wizard
        ↓
  Planning Engine
        ↓
  Mission Package
        ↓
      Runtime
        ↓
     Provider
        ↓
Engineering Artifact
```

For an in-depth breakdown of system boundaries and Clean Architecture, refer to the [Architecture Guide](docs/architecture.md).

## 8. CLI Reference

FlowForge provides a streamlined command-line interface for managing the entire lifecycle.

- `flowforge init`: Initialize a workspace.
- `flowforge doctor`: Diagnose environment and provider health.
- `flowforge mission new`: Launch the authoring wizard.
- `flowforge compile <ID>`: Compile a mission package.
- `flowforge run <ID>`: Execute a compiled package.

For all commands and options, consult the [Detailed CLI Reference](docs/cli.md).

## 9. Project Structure

FlowForge structures your repository to enforce separation of engineering memory from source code:

```
engineering/
├── missions/
│   ├── backlog/       # Planned missions
│   ├── active/        # Active missions being executed
│   ├── completed/     # Successfully completed missions
├── rfcs/              # Project Requests for Comments
├── adrs/              # Architecture Decision Records
└── PROJECT_STATE.yaml # Long-term engineering memory
```

## 10. Provider Architecture

FlowForge is strictly provider-independent. AI execution engines are configured declaratively in a `providers.yaml` file, ensuring your workspace never gets locked into a specific vendor's SDK or API.

## 11. Roadmap

FlowForge is currently in the **Product Core** phase, polishing the framework for the upcoming `v1.0.0-beta` release.

- **Engineering Core**: (Completed) Mission Planning, Runtime, Workspace, Artifact Identity.
- **Product Core**: (Active) Documentation, Distribution, Release Preparation.
- **FlowForge Labs**: (Future) Dashboards, VS Code Extensions, Cloud Integrations.

See [ROADMAP.md](ROADMAP.md) for full details.

## 12. Contributing

We welcome contributions! FlowForge enforces Clean Architecture and SOLID principles. During the current Product Core phase, we are strictly focused on quality, testing, and developer experience. No new engineering capabilities are being accepted.

Please review our [AI Contribution Guide](CONTRIBUTING_AI.md) before submitting pull requests.

## 13. License

FlowForge is open-source software licensed under the [MIT License](LICENSE).
