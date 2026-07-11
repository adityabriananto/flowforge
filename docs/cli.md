# CLI Reference

FlowForge provides a suite of CLI commands for orchestrating the engineering lifecycle.

*Note: This documentation reflects the commands as implemented in FlowForge Core v1.0.0-beta.*

---

## `flowforge init`
Initializes an Engineering Workspace in the current directory.
- **What it does:** Creates the `engineering/` and `.flowforge/` directories, detects the project's framework, and sets up `PROJECT_STATE.yaml`.
- **Usage:** `flowforge init`

---

## `flowforge doctor`
Diagnoses the environment to ensure FlowForge can run.
- **What it does:** Checks Python versions, required dependencies, workspace health, and validates Provider configurations in `providers.yaml`.
- **Usage:** `flowforge doctor`

---

## `flowforge mission new`
Launches the Interactive Mission Authoring Wizard.
- **What it does:** Prompts the developer for a Mission Title, Business Goal, and Priority. It outputs a standardized Mission YAML file into `engineering/missions/backlog/`.
- **Usage:** `flowforge mission new`
- **Optional arguments:** `flowforge mission new "Implement OAuth" --desc "Add Google Login"` (bypasses interactive mode).

---

## `flowforge mission list`
Lists all missions in the workspace.
- **What it does:** Displays missions grouped by their lifecycle status (`BACKLOG`, `ACTIVE`, `COMPLETED`).
- **Usage:** `flowforge mission list`

---

## `flowforge compile <MISSION_ID>`
Compiles a raw mission into an executable Mission Package.
- **What it does:** Merges the raw backlog mission with the Planning Context (framework, architecture, project state) to generate a heavily detailed, vendor-neutral execution plan.
- **Usage:** `flowforge compile PROJECT-000`

---

## `flowforge mission start <MISSION_ID>`
Transitions a mission from the backlog to active status.
- **What it does:** Moves the mission file into the `active/` directory, signaling that execution is imminent.
- **Usage:** `flowforge mission start PROJECT-000`

---

## `flowforge run <MISSION_ID>`
Executes a compiled Mission Package.
- **What it does:** Invokes the Runtime Engine, which delegates the package to the configured Provider. Records an immutable Engineering Session log.
- **Usage:** `flowforge run PROJECT-000`

---

## `flowforge mission complete <MISSION_ID>`
Finalizes an active mission.
- **What it does:** Moves the mission to the `completed/` directory and permanently updates `PROJECT_STATE.yaml` with the knowledge gained during execution.
- **Usage:** `flowforge mission complete PROJECT-000`
