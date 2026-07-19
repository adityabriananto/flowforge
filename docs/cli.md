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
- **What it does:** Creates a provider configuration YAML file in `.flowforge/providers/`. Starting in recent updates, you can safely store your raw `api_key` directly in this file since the `.flowforge/` directory is git-ignored, eliminating the need to set environment variables on every terminal session.
- **Wizard Questions:**
  1. **Select adapter:** (e.g., `GoogleGeminiAPIProviderAdapter`, `OpenAIAPIProviderAdapter`, `LocalSubprocessAdapter`)
  2. **Enter connection name:** A unique ID for this connection (e.g., `gemini-main`).
  3. **Configure properties:** Depending on the adapter, you will be asked for parameters like `api_key` or `command`.
- **Example:**
  ```bash
  $ flowforge provider add
  Select adapter: GoogleGeminiAPIProviderAdapter
  Enter connection name: gemini-main
  api_key [current: None]: AIzaSyBx...
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
- **Wizard Questions:**
  1. **Enter profile name:** (e.g., `executor`, `reviewer`).
  2. **Select provider:** Choose from previously configured providers (e.g., `gemini-main`).
  3. **Enter model:** The exact API model string (e.g., `gemini-1.5-pro`, `gpt-4o`). Note: Using full reasoning models like `gemini-1.5-pro` is strongly recommended for autonomous coding tasks.
- **Example:**
  ```bash
  $ flowforge profile add
  Enter profile name: executor
  Select provider: gemini-main
  Enter model: gemini-1.5-pro
  ```

### `flowforge profiles`
Lists all configured execution profiles.
- **Example:**
  ```bash
  $ flowforge profiles
  Available Profiles:
  - executor (Provider: gemini-main, Model: gemini-1.5-pro)
  ```

---

## Mission Lifecycle

### `flowforge mission new`
Launches the Interactive Mission Authoring Wizard to create a new requirement.
- **What it does:** Prompts the developer for structured inputs to generate a comprehensive Mission YAML file in `engineering/missions/backlog/`. The wizard supports English prompts and robust cancellation handling.
- **Wizard Questions (Prepare your answers):**
  1. **Mission Title:** A short, descriptive name for the task (e.g., `Add login page`).
  2. **Project Goal:** The primary objective of what needs to be achieved in this mission.
  3. **Business Context:** Why this mission matters or how it fits into the broader application.
  4. **Target Users:** Who will be using this feature.
  5. **Priority:** Select between `Low`, `Medium`, or `High`.
- **Example:**
  ```bash
  $ flowforge mission new
  Enter title: Implement User Dashboard
  Enter Project Goal: Create a dashboard to display user statistics.
  Enter Business Context: Allows admins to track daily active usage.
  Enter Target Users: System Administrators.
  Priority (Low/Medium/High): High
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
- **What it does:** Invokes the Runtime Engine, which delegates the package to the configured Profile. Parses the AI's XML response to apply file changes and generate an Implementation Report in `engineering/reports/`. The CLI output explicitly lists both `Artifacts Produced (Reports)` and `Files Changed (Code)`.
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
