# Engineering Strategy — Core Completion Roadmap

## Product Philosophy

FlowForge Core should remain the minimum platform required to:
- create engineering missions
- preserve engineering knowledge
- execute engineering work
- resume engineering sessions
- support multiple providers

Everything beyond these core capabilities (e.g., visual interfaces, complex analytics, marketplace) should be treated as optional productivity enhancements that reside outside the Core platform.

## Core Completion Targets

The FlowForge Core platform is considered complete for the initial `v1.0.0-beta` release upon the completion of the following specific missions:

- **FF-024**: Engineering Artifact Identity Service *(Completed)*
- **FF-025**: Mission Planning Engine
- **FF-026**: README 2.0 & Developer Onboarding
- **FF-027**: Public Distribution (PyPI)

## Core Freeze Policy

Once **FF-027** is completed, the FlowForge Core enters a frozen state.

### Allowed in Core:
- Critical bug fixes
- Security fixes
- Performance improvements
- Documentation improvements
- Small compatibility updates

### NOT Allowed in Core (Belongs in Applications / Plugins):
- Experimental features
- UX experiments
- Dashboard functionality
- Visual editors
- Cloud integrations
- AI-assisted planning
- Marketplace integrations

## Branching Strategy

The repository utilizes two long-lived branches to isolate stability from future evolution:

- `main`: Represents the stable FlowForge Core. Only validated, production-ready features that align with the Core Freeze policy are merged here.
- `next`: Represents the future evolution of FlowForge. Experimental features, dashboards, cloud services, and marketplace mechanics are implemented and validated here before consideration as independent applications.
