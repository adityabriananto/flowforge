# FlowForge Product Roadmap

The development release roadmap for the FlowForge orchestration framework.

---

## Release Roadmap

### Engineering Core (Completed)
**Missions: FF-012 ~ FF-025**

Focus was on solidifying the internal State Machine architecture, unifying AI input/output standards, and introducing deterministic engineering workflows.
- **Platform Validation**: The Engine Layer has been validated via pilot projects (BroDev Cashier & Meeting Intelligence).
- **Engineering Workspace**: Standardized directory structure for persistent engineering memory.
- **Mission Planning Engine**: Deterministic engineering planning without relying directly on AI execution.
- **Mission Lifecycle**: Structured flow of engineering units from Backlog to Active to Completed.
- **Artifact Identity Service**: Engineering identifier management across repositories.

### Product Core (Current Phase)
**Missions: FF-026 ~ FF-029**

Focus is on polishing the platform for public adoption, validating documentation, packaging, and certifying the Core platform. **No new engineering capabilities will be introduced in this phase.**
- **FF-026 Documentation & Developer Onboarding**: (Completed) Rebuilding the installation guide, onboarding workflow, and concepts.
- **FF-027 Public Distribution**: (Current) Preparing for PyPI package release.
- **FF-028 Release Preparation**: Final adjustments for stability.
- **FF-029 Core Audit & Beta Certification**: Deep audit of Clean Architecture boundaries and testing coverage.

### FlowForge v1.0.0-beta
The culmination of the Product Core phase. The FlowForge framework will be officially published and enter a public beta period. 

### Core Freeze Policy
Once FlowForge reaches v1.0.0-beta, the core repository (`main` branch) enters the **Core Freeze** phase.
- **The Core WILL accept**: Critical bug fixes, Security fixes, Performance improvements, Documentation improvements, Small compatibility updates.
- **The Core WILL NOT accept**: Experimental features, UX dashboards, visual editors, cloud integrations, AI-assisted planning, or marketplaces. All advanced capabilities must be developed on application layers outside the Core.

### FlowForge Labs (Future Evolution)
Focus shifts to distributed infrastructure, expanding the developer ecosystem, and UX experiments (developed strictly outside the frozen Core).
- **Marketplace**: Plugin stores and shareable custom worker templates.
- **Cloud Integration**: SaaS-managed FlowForge instances.
- **VSCode Extension**: Visual editor extension to design workflows and monitor instance statuses directly from the IDE.
- **Model Context Protocol (MCP)**: Full standard support for MCP to integrate external AI tools.
- **AI-assisted Planning (Plugin)**: Integrating artificial intelligence directly into the authoring process as an extension module.

---

## Definition of Done (DoD)

-   All unit & integration tests pass at 100%.
-   API Documentation, README, and STATUS are updated in English.
-   ADRs are created/updated for all new architectural decisions.
-   All code compiles successfully without warnings or errors.
-   Changes are pushed to the remote origin repository.
