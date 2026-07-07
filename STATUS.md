# Project Status

## Project

FlowForge

## Version

v0.1.0

## Current Sprint

Sprint 11 -- Refactor & Foundation (v1.1)

## Overall Progress

100% (v1.1 Foundation Complete)

## Completed

-   Product Vision
-   Sprint Roadmap
-   ADR-001 Vendor Agnostic
-   ADR-002 Framework Agnostic Core
-   Technology Stack
-   Business Requirements Document (BRD)
-   Product Requirements Document (PRD) (termasuk User Persona, Scope, dan Success Metrics)
-   Sprint 0 Completion Review
-   ADR-003 State Machine Engine Core Design (Pure Custom Lightweight)
-   ADR-004 Event-Driven Architecture Design (Ports & Adapters)
-   Hexagonal Architecture Diagram & Directory Layout Concept
-   Sprint 1 Completion Review & Architecture Sign-off
-   Core Domain Model (entities: Workflow, WorkflowInstance, Job, Event) di `src/flowforge/domain/models.py`
-   Lightweight State Machine Engine logic di `src/flowforge/domain/engine.py`
-   Unit Testing suite (`pytest`) untuk State Machine di `tests/test_engine.py`
-   Sprint 2 Completion Review & Domain Model Sign-off
-   Asynchronous Database Connection Setup (SQLAlchemy 2.x + Fallback SQLite) di `src/flowforge/adapters/database/database.py`
-   Declarative DB ORM Models (WorkflowDB, WorkflowInstanceDB, JobDB, EventDB) di `src/flowforge/adapters/database/db_models.py`
-   Database Repository Port (abstract interface) di `src/flowforge/ports/database.py`
-   SQLAlchemyRepository Adapter implementation di `src/flowforge/adapters/database/repository.py`
-   Database Integration Tests suite (`pytest-asyncio` + `aiosqlite`) di `tests/test_repository.py`
-   Sprint 3 Completion Review & Database Integration Sign-off
-   Worker Runtime Port (abstract interface) di `src/flowforge/ports/worker.py`
-   SubprocessWorkerRuntime Adapter implementation (isolated env + async execution) di `src/flowforge/adapters/worker/subprocess_runtime.py`
-   Worker Runtime unit tests suite (`pytest-asyncio`) di `tests/test_worker_runtime.py`
-   Sprint 4 Completion Review & Worker Runtime Sign-off
-   LLM Connector Port (abstract interface) di `src/flowforge/ports/connector.py`
-   ClaudeConnector Adapter implementation (Anthropic API messages endpoint) di `src/flowforge/adapters/connector/claude_connector.py`
-   CodexConnector Adapter implementation (OpenAI chat completions endpoint) di `src/flowforge/adapters/connector/codex_connector.py`
-   LLM Connectors unit tests suite with mock server requests (`pytest-httpx`) di `tests/test_connectors.py`
-   Sprint 5 Completion Review & Connectors Sign-off
-   Pydantic API request/response schemas di `src/flowforge/entrypoints/api/schemas.py`
-   WebSocket connection manager (push-only live sync) di `src/flowforge/entrypoints/api/websocket_manager.py`
-   FastAPI router (Workflows, Instances, Transitions, Events endpoints) di `src/flowforge/entrypoints/api/router.py`
-   FastAPI application setup & database auto-init di `src/flowforge/entrypoints/api/main.py`
-   REST API HTTP & WebSocket Integration Tests suite (`fastapi.testclient`) di `tests/test_api.py`
-   Sprint 6 Completion Review & REST API Sign-off
-   Vite React + TypeScript app scaffolding di `dashboard/`
-   Custom WebSocket hook (`useWorkflowWS`) untuk real-time state sync di `dashboard/src/hooks/useWorkflowWS.ts`
-   State Machine monitoring visual (`WorkflowGraph.tsx`) di `dashboard/src/components/WorkflowGraph.tsx`
-   Split diff viewer (`DiffViewer.tsx`) di `dashboard/src/components/DiffViewer.tsx`
-   Interactive HITL approval panel (`ApprovalPanel.tsx`) di `dashboard/src/components/ApprovalPanel.tsx`
-   Custom local SVG Icons helper (`Icons.tsx`) di `dashboard/src/components/Icons.tsx`
-   Main App layout integration & premium glassmorphism styling di `dashboard/src/App.tsx` dan `dashboard/src/index.css`
-   Sprint 7 Completion Review & React Dashboard Sign-off
-   Git Remote origin configuration di `g:/Development/agent-interface/`
-   Git Service port (`GitService`) dan subprocess adapter (`SubprocessGitService`)
-   Git integration tests suite (`pytest`) di `tests/test_git_service.py`
-   Sprint 8 Completion Review & Git Integration Sign-off
-   Plugin base class (`FlowForgePlugin`) dan manager (`PluginManager`)
-   Plugin SDK lifecycle hooks unit tests suite (`pytest`) di `tests/test_plugin_sdk.py`
-   Sprint 9 Completion Review & Plugin SDK Sign-off
-   Audit keamanan API Key log masking & sanitasi codebase
-   README & STATUS v1.0.0 update
-   Sprint 10 Completion Review & Production Ready Sign-off
-   State Machine Transition Table implementation di `src/flowforge/domain/engine.py`
-   YAML Workflow Loader (`yaml_loader.py`) di `src/flowforge/domain/yaml_loader.py`
-   Capability Resolver (`capability_resolver.py`) untuk dynamic LLM providers
-   Prompt Builder & Context Loader (`prompt_builder.py`) terpusat
-   Artifact Manager (`artifact_manager.py`) untuk AI output tracking
-   Memory Module (`memory.py`) untuk short & long-term memory
-   Auto-Discovery Plugins via pip entrypoints (`importlib.metadata`)
-   Workflow Timeline & Execution Metrics di React Dashboard
-   v1.1 Refactor unit testing suite (`pytest`) di `tests/test_v1_1_refactor.py`

## Current Task

-   v1.1 Release Sign-off

## Next Tasks

-   Sprint 12 -- Resiliency & Scheduling (v1.2) (Multi worker, retry, scheduler, timeout, queue)

## Blockers

None

## Decision Log

-   Python sebagai backend
-   React sebagai frontend
-   Core harus framework agnostic
-   AI menggunakan Agent Interface
-   Workflow definition menggunakan format YAML
-   Isolasi runtime Worker fase awal menggunakan subprocess Python terisolasi
-   State Machine Engine menggunakan pure custom lightweight implementation
-   Event-driven communication menggunakan pola Ports & Adapters (InMemory/Redis PubSub)
-   LLM Connectors menggunakan Claude (Anthropic API) dan Codex (OpenAI API) yang terintegrasi secara asinkron via httpx dengan log masking API Key yang aman
-   REST API diimplementasikan menggunakan FastAPI dengan WebSocket push-only real-time notification untuk perubahan status instansi workflow
-   React Dashboard diimplementasikan menggunakan Vite + TypeScript, Zustand state, custom local SVG Icons (bebas dari error bundler Rolldown), serta visualisasi UI premium dark-mode glassmorphism dan micro-animations untuk interaksi HITL dan monitoring audit trail.
