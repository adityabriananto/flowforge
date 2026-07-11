# Concepts & Glossary

This document serves as the canonical reference for FlowForge terminology.

### Engineering Workspace
The foundational directory structure (`engineering/`) injected into a repository by FlowForge. It acts as the permanent, file-based memory of the software project, ensuring engineering knowledge outlives volatile AI sessions.

### Mission
A declarative unit of engineering work. Rather than prompt hacking, developers write Missions containing clear Business Goals. Missions flow through a lifecycle (`BACKLOG` -> `ACTIVE` -> `COMPLETED`).

### Planning Context
A unified, deterministic snapshot of the current state of the repository, including the framework, language, recently completed missions, and the current project phase. It is gathered automatically by FlowForge before a mission is compiled.

### Mission Package
A compiled, vendor-agnostic bundle of instructions. It merges the raw Mission intent with the Planning Context and relevant architecture documents. It represents the final instructions that will be handed to the AI.

### Runtime
The stateless execution engine in FlowForge. It accepts a Mission Package and orchestrates its execution, handling logging and session management without being coupled to any specific AI vendor.

### Provider
An abstraction layer (adapter) that represents a specific AI execution driver (e.g., an Anthropic Claude agent, an OpenAI agent, or a local Ollama model).

### Engineering Session
An immutable, granular log file created during the execution of a Mission. It tracks exactly what the Provider did, what files were changed, and what commands were run. If an AI breaks the build, the Engineering Session provides a complete audit trail.

### Engineering State
The single source of truth for the project's long-term memory (`PROJECT_STATE.yaml`). It tracks high-level architectural knowledge, completed missions, and current blockers.

### Engineering Artifact
The tangible output produced by a Mission. This includes code changes, tests, updated documentation, or a new architecture decision record (ADR).

### Engineering Identity
The human-facing canonical identifier (e.g., `PROJECT-004`). Used exclusively in CLI outputs, communication, documentation, and file names (like Mission Packages) to ensure usability.

### System Identity
The internal identifier (e.g., UUID). Used strictly for persistence, caching, and repository integrity under the hood. Developers should rarely need to interact with UUIDs.
