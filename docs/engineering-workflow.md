# Engineering Workflow & Guides

This document explains the recommended engineering workflow discovered during real-world validation, the roles involved, and the principles underlying FlowForge.

## Recommended Engineering Workflow

FlowForge intentionally does not enforce a rigid workflow. Teams may adapt the workflow to fit their own engineering governance. However, the following is the recommended workflow observed to produce the best outcomes:

`	ext
Mission
   ?
Mission Package
   ?
Executor
   ?
Implementation
   ?
Engineering Review
   ?
Approved?
   ?
flowforge mission complete
   ?
Git Commit
   ?
Git Push
`

## Mission Lifecycle

The Mission Lifecycle defines the state of a single unit of work in FlowForge. Missions transition through states:
- **BACKLOG**: A planned mission that is not yet ready for execution.
- **ACTIVE**: A mission currently being executed by the AI provider.
- **COMPLETED**: A mission that has successfully passed Engineering Review and has been marked complete.

## Engineering Roles

Within the Engineering Workflow, distinct responsibilities are distributed among the team:

### Engineering Lead
Responsible for:
- Roadmap planning
- Mission authoring
- Mission sequencing
- Mission approval
- Starting the next mission

### FlowForge
Responsible for:
- Planning Context resolution
- Mission Lifecycle management
- Mission Package compilation
- Engineering orchestration

### Executor (AI Provider)
Responsible for:
- Implementation of the mission goals
- Testing (writing and executing unit tests)
- Documentation updates within the project

### Engineering Reviewer
Responsible for:
- Architecture review
- Scope validation
- Business logic validation
- Engineering quality assurance

## Engineering Principles

The following principles have emerged from real-world validation and guide the development and usage of FlowForge:

1. **FlowForge orchestrates engineering work, not engineering authority.** The tool manages the state, but human developers define the goals and make critical architectural decisions.
2. **Engineering review is recommended before mission completion.** Do not automatically mark missions complete; always review the generated output.
3. **Mission completion represents engineering approval.** It signals that the deliverables meet the project's quality standards.
4. **Engineering Lead decides when the next mission begins.** Execution is pull-based, driven by the Lead.
5. **Tool upgrades should remain backward compatible whenever reasonably possible.** Engineering workspaces should rarely require manual migration.
