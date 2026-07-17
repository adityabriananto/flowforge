# CLI Reference

FlowForge provides a suite of CLI commands for orchestrating the engineering lifecycle.

*Note: This documentation reflects the commands as implemented in FlowForge Core v1.0.0-beta.*

---

## Workspace Management

### `flowforge init`
Initializes an Engineering Workspace in the current directory.
- **What it does:** Creates the `engineering/` documentation directory and `.flowforge/` system directory, detects the project's framework, and sets up `PROJECT_STATE.yaml`.
- **Example:**
  ```bash
  $ flowforge init
  [OK] Initialized Engineering Workspace in current directory.
  [OK] Detected framework: React
  ```

### `flowforge doctor`
Diagnoses the environment to ensure FlowForge can run.
- **What it does:** Checks Python versions, required dependencies, workspace health, and validates Provider configurations.
- **Example:**
  ```bash
  $ flowforge doctor
  [OK] Python Version: 3.10
  [OK] Workspace Detected: Yes
  ```

---

## Infrastructure Configuration

FlowForge separates the API connection (Provider) from the specific model execution constraints (Profile).

### `flowforge provider add`
Launches the wizard to configure a new AI Provider (e.g., Gemini, OpenAI, Subprocess).
- **Example:**
  ```bash
  $ flowforge provider add
  Select adapter: GoogleGeminiAPIProviderAdapter
  Enter connection name: gemini-main
  ```

### `flowforge providers`
Lists all configured providers.
- **Example:**
  ```bash
  $ flowforge providers
  Available Providers:
  - gemini-main (GoogleGeminiAPIProviderAdapter)
  ```

### `flowforge profile add`
Launches the wizard to create an execution Profile tied to a specific Provider.
- **Example:**
  ```bash
  $ flowforge profile add
  Enter profile name: executor
  Select provider: gemini-main
  Enter model: gemini-3.1-flash-lite
  ```

### `flowforge profiles`
Lists all configured execution profiles.
- **Example:**
  ```bash
  $ flowforge profiles
  Available Profiles:
  - executor (Provider: gemini-main, Model: gemini-3.1-flash-lite)
  ```

---

## Mission Lifecycle

### `flowforge mission new`
Launches the Interactive Mission Authoring Wizard to create a new requirement.
- **What it does:** Prompts the developer for a Mission Title, Business Goal, and Priority. It outputs a standardized Mission YAML file into `engineering/missions/backlog/`.
- **Example:**
  ```bash
  $ flowforge mission new
  Enter title: Add login page
  [OK] Created mission PROJECT-001 in backlog.
  ```

### `flowforge compile <MISSION_ID>`
Compiles a raw mission into an executable Mission Package.
- **What it does:** Merges the raw backlog mission with the Planning Context (framework, architecture, project state) and Engineering Contract to generate a `.package.yaml` file in `.flowforge/packages/`.
- **Example:**
  ```bash
  $ flowforge compile PROJECT-001
  [OK] Compiled PROJECT-001 successfully.
  ```

### `flowforge mission start <MISSION_ID>`
Transitions a mission from the backlog to active status.
- **What it does:** Moves the mission file into the `active/` directory, signaling that execution is imminent.
- **Example:**
  ```bash
  $ flowforge mission start PROJECT-001
  [OK] Mission PROJECT-001 is now ACTIVE.
  ```

### `flowforge run <MISSION_ID> --profile <PROFILE>`
Executes a compiled Mission Package using an AI Provider.
- **What it does:** Invokes the Runtime Engine, which delegates the package to the configured Profile. Parses the AI's XML response to apply file changes and generate an Implementation Report.
- **Example:**
  ```bash
  $ flowforge run PROJECT-001 --profile executor
  [FlowForge CLI] Initiating runtime engine for mission: PROJECT-001
  [FlowForge CLI] Execution successful.
  ```

### `flowforge mission complete <MISSION_ID>`
Finalizes an active mission after human review.
- **What it does:** Moves the mission to the `completed/` directory and permanently updates `PROJECT_STATE.yaml` with the knowledge gained during execution.
- **Example:**
  ```bash
  $ flowforge mission complete PROJECT-001
  [OK] Mission PROJECT-001 moved to completed.
  ```
