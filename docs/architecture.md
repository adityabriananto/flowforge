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

## 2. Planning vs. Runtime Separation

The most critical architectural boundary in FlowForge is the absolute separation of **Planning** and **Execution (Runtime)**.

### Planning Engine
The Planning Engine is responsible for capturing human intent (the Business Goal) and translating it into a highly structured `MissionPackage`. The Planning Engine uses deterministic rules and workspace context to generate this package. **It does not execute code.**

### Runtime Engine
The Runtime Engine is completely stateless. It accepts a `MissionPackage` and orchestrates its execution. The Runtime does not know *what* it is building; it only knows *how* to delegate the instructions to an AI Provider.

## 3. Provider Abstraction

FlowForge avoids vendor lock-in through the **Provider** abstraction.
The Runtime communicates with execution drivers (e.g., Claude, Ollama, OpenAI) via a standardized Port interface. Providers are adapters that translate FlowForge's execution commands into vendor-specific API calls. 

Because the `MissionPackage` is completely vendor-neutral, any AI provider can theoretically execute any mission, provided it has sufficient reasoning capability.

## 4. Engineering Workspace

The Engineering Workspace is the persistent storage layer (`engineering/` folder). It holds:
- **PROJECT_STATE.yaml**: The central, mutable Engineering State.
- **Missions**: YAML files representing units of work.
- **ADRs & RFCs**: Immutable records of architectural decisions.

The workspace acts as the long-term memory of the project.

## 5. Mission Lifecycle

Missions transition through three strict states:
1. **BACKLOG**: The mission has been drafted but not executed.
2. **ACTIVE**: The mission is currently assigned to a Provider via the Runtime.
3. **COMPLETED**: The AI has delivered the artifact, the Developer has approved it, and the `PROJECT_STATE.yaml` has been updated with the mission's outcomes.

## 6. Execution Pipeline

When `flowforge run` is triggered:
1. The **Runtime** loads the compiled `MissionPackage`.
2. The Runtime instantiates an **Engineering Session**.
3. The Runtime invokes the configured **Provider**.
4. The Provider modifies the codebase.
5. The Runtime logs all changes, terminal outputs, and decisions into the Session log.
6. The session concludes, awaiting developer review.
