# Architecture Guide

This document is intended for maintainers and contributors. It describes the internal architecture of FlowForge Core.

## 1. System Architecture & Boundaries

FlowForge is designed strictly following **Clean Architecture** (Ports and Adapters) principles. The core domain never depends on external APIs, specific AI SDKs, or database drivers.

### The Execution Pipeline

```text
    Developer
        ↓
  Mission Wizard
        ↓
  Planning Engine (Compiler)
        ↓
  Mission Package
        ↓
      Runtime
        ↓
      Provider (Adapter)
        ↓
 XML Output Parsing
        ↓
Engineering Artifact
```

## 2. Planning vs. Runtime Separation

The most critical architectural boundary in FlowForge is the absolute separation of **Planning** and **Execution (Runtime)**.

### Planning Engine (Compiler)
The Planning Engine is responsible for capturing human intent (the Business Goal) via the Mission Wizard and translating it into a highly structured `.package.yaml`. The compiler uses deterministic rules and workspace context to generate this package. **It does not execute code.**

### Runtime Engine
The Runtime Engine is completely stateless. It accepts a `MissionPackage` and orchestrates its execution. The Runtime does not know *what* it is building; it only knows *how* to delegate the instructions to an AI Provider.

## 3. Provider Architecture

FlowForge avoids vendor lock-in through the **Provider** abstraction.
The Runtime communicates with execution drivers (e.g., Google Gemini, OpenAI, or a local Subprocess CLI) via a standardized Port interface. Providers are simply adapters that translate FlowForge's execution commands into vendor-specific API calls. 

FlowForge is **not an AI model catalog**. Instead, developers define API keys and driver types in `.flowforge/providers/`. Any AI provider can theoretically execute any mission as long as it respects the standard XML-wrapped output parsing mechanism.

## 4. Profile Architecture

Profiles map a specific role (e.g., "executor" or "architect") to a specific Provider and model (e.g., `gemini-main` using `gemini-3.1-flash-lite`). Profiles are stored in `.flowforge/profiles/`. This decouples the mission from the underlying hardware or service, allowing users to swap models at runtime (`--profile executor`).

## 5. Engineering Workspace & Detection

The Engineering Workspace is the persistent storage layer (`engineering/` folder). It holds:
- **PROJECT_STATE.yaml**: The central, mutable Engineering State.
- **Missions**: YAML files representing units of work.
- **Reports**: AI-generated Implementation Reports in `engineering/reports/`.
- **ADRs & RFCs**: Immutable records of architectural decisions.

The `.flowforge/` system folder is ephemeral (automatically git-ignored) and handles:
- **Mission Packages**: Compiled instructions in `.flowforge/packages/`.
- **Provider & Profile Configs**: YAML files storing models and API keys (e.g. `api_key`).

FlowForge uses automatic Workspace Detection. Commands like `flowforge run` search upwards for the `.flowforge` directory to ensure they run in the correct context.

## 6. Mission Lifecycle

Missions transition through three strict states:
1. **BACKLOG**: The mission has been drafted via the Mission Wizard but not compiled/executed.
2. **ACTIVE**: The mission is compiled into a Mission Package and assigned to a Provider via the Runtime.
3. **COMPLETED**: The AI has delivered the Implementation Report, the Developer has approved the XML-parsed file changes, and the mission is formally completed via `flowforge mission complete`.

## 7. Execution Pipeline

When `flowforge run` is triggered:
1. The **Runtime** loads the compiled `MissionPackage`.
2. The Runtime instantiates an **Engineering Session**.
3. The Runtime invokes the configured **Provider**.
4. The Provider generates the output (typically an XML-wrapped response).
5. The Runtime parses the XML output and writes the physical file changes and Implementation Report to disk.
6. The session concludes, awaiting developer review.
