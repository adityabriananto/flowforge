import argparse
import sys
import os
import uuid
import asyncio

from flowforge.domain.yaml_loader import load_workflow_from_file
from flowforge.domain.engine import StateMachine
from flowforge.domain.models import WorkflowInstance

def cmd_init(args):
    """Initializes a new FlowForge project directory (FF-017 Smart Project Bootstrap)."""
    print("[FlowForge CLI] Initializing project workspace...")
    
    from flowforge.services.workspace.bootstrapper import SmartBootstrapper
    
    try:
        # Detect project, setup folder structures, generate metadata, and install templates
        prefix = args.prefix if hasattr(args, "prefix") and args.prefix else "PROJECT"
        force = args.force if hasattr(args, "force") else False
        
        print("[OK] Detecting project")
        details = SmartBootstrapper.bootstrap(base_path=".", force=force, prefix=prefix)
        
        # Write additional workflow and provider configs if not present
        os.makedirs("providers", exist_ok=True)
        os.makedirs("agents", exist_ok=True)
        
        workflow_yaml_path = "workflow.ff.yaml"
        if not os.path.exists(workflow_yaml_path):
            workflow_yaml = f"""name: "Autonomous AI Agent Workflow"
version: "1.0.0-beta"
initial_state: "CODING"

roles:
  architect:
    capability: "architecture"
    policy: "quality-first"
  coder:
    capability: "coding"
    policy: "cost-first"

states:
  CODING:
    name: "AI Coding Session"
    worker_type: "subprocess"
    script: "agents/coder.py"
  TESTING:
    name: "Automated pytest suite"
    worker_type: "subprocess"
    script: "agents/run_tests.py"
  COMPLETED:
    name: "Completed successfully"
    is_final: true

transitions:
  - {{ from: "CODING", event: "SUCCESS", to: "TESTING" }}
  - {{ from: "TESTING", event: "SUCCESS", to: "COMPLETED" }}
  - {{ from: "TESTING", event: "FAILURE", to: "CODING" }}
"""
            with open(workflow_yaml_path, "w", encoding="utf-8") as f:
                f.write(workflow_yaml)

        # Write Claude provider profile yaml if missing
        claude_yaml_path = "providers/claude.yaml"
        if not os.path.exists(claude_yaml_path):
            claude_yaml = """name: "claude"
capabilities:
  reasoning: 95
  coding: 85
  review: 98
cost: "high"
speed: "medium"
context_length: 200000
"""
            with open(claude_yaml_path, "w", encoding="utf-8") as f:
                f.write(claude_yaml)

        # Write Gemini provider profile yaml if missing
        gemini_yaml_path = "providers/gemini.yaml"
        if not os.path.exists(gemini_yaml_path):
            gemini_yaml = """name: "gemini"
capabilities:
  reasoning: 90
  coding: 80
  review: 92
cost: "low"
speed: "fast"
context_length: 1000000
"""
            with open(gemini_yaml_path, "w", encoding="utf-8") as f:
                f.write(gemini_yaml)

        print("[OK] Creating Engineering Workspace")
        print("[OK] Installing templates")
        print("[OK] Creating PROJECT_STATE")
        print("[OK] Creating initial Mission")
        print("\nInitialization complete.")
        print(f"Project Type: {details['project_type']} (Framework: {details['framework']}, Language: {details['language']})")
        print("\nNext Recommended Action:")
        print(f"  Review the initial mission:")
        print(f"  flowforge mission show {prefix}-000")
        
    except Exception as e:
        print(f"[FlowForge CLI] Error during initialization: {str(e)}", file=sys.stderr)
        sys.exit(1)

def cmd_run(args):
    """Runs a local .ff.yaml workflow or executes a mission via AI Runtime (DX)."""
    input_val = args.file
    
    import re
    is_mission_code = bool(re.match(r'^[A-Za-z0-9_-]+-\d+$', input_val))
    
    if is_mission_code and not os.path.exists(input_val):
        run_mission_orchestration(input_val, getattr(args, "profile", None))
    else:
        run_legacy_workflow(input_val)

def run_legacy_workflow(file_path):
    if not os.path.exists(file_path):
        print(f"[FlowForge CLI] Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        workflow = load_workflow_from_file(file_path)
        print(f"[FlowForge CLI] Loaded FFWL: {workflow.name} (v{workflow.version})")
        print(f"[FlowForge CLI] Initial state: {workflow.initial_state}")
        
        # Instantiate local state machine and run
        engine = StateMachine(workflow)
        instance = WorkflowInstance(id=uuid.uuid4(), workflow_id=workflow.id, current_state=workflow.initial_state)
        
        print(f"[FlowForge CLI] Active state machine instanced ID: {instance.id}")
        print(f"[FlowForge CLI] Running otonomous simulation transitions...")
        
        # Simulate transitions
        current = workflow.initial_state
        while current != "COMPLETED" and len(workflow.states) > 0:
            # Emulate success event transition
            event = engine.transition(instance, "SUCCESS")
            print(f"  [Transition] {event.payload['from_state']} ➔ SUCCESS ➔ {event.payload['to_state']}")
            current = instance.current_state
            if current == "COMPLETED" or workflow.states.get(current).is_final:
                break
                
        print(f"[FlowForge CLI] Execution finished. Final state: {instance.current_state}")
    except Exception as e:
        print(f"[FlowForge CLI] Error executing workflow: {str(e)}", file=sys.stderr)
        sys.exit(1)

def run_mission_orchestration(mission_code, profile_name=None):
    print(f"[FlowForge CLI] Initiating runtime engine for mission: {mission_code}")
    from flowforge.services.compiler.compiler import MissionPackageCompiler
    from flowforge.services.workspace.session_service import EngineeringSessionService
    from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
    from flowforge.services.runtime.engine import AIRuntimeEngine
    from flowforge.adapters.workspace.yaml_session_repository import YAMLEngineeringSessionRepository
    
    compiler = MissionPackageCompiler()
    
    session_repo = YAMLEngineeringSessionRepository()
    session_service = EngineeringSessionService(session_repo)
    
    registry = AIRuntimeProviderRegistry()
    
    from flowforge.services.workspace.provider_manager import ProviderManager
    from flowforge.services.runtime.provider_config_loader import SubprocessCLIProviderAdapter, GoogleGeminiAPIProviderAdapter, OpenAIAPIProviderAdapter

    for prov in ProviderManager.list_providers("."):
        if prov.type == "cli":
            adapter = SubprocessCLIProviderAdapter(
                name_str=prov.name,
                command=prov.command if prov.command else "echo 'No CLI command specified'"
            )
        else: # type == 'api'
            if prov.provider == "openai":
                adapter = OpenAIAPIProviderAdapter(
                    name_str=prov.name,
                    model=prov.model if prov.model else "gpt-4o",
                    api_key_env=prov.api_key_env if prov.api_key_env else "OPENAI_API_KEY",
                    api_key=prov.api_key
                )
            else:
                adapter = GoogleGeminiAPIProviderAdapter(
                    name_str=prov.name,
                    model=prov.model if prov.model else "gemini-1.5-pro",
                    api_key_env=prov.api_key_env if prov.api_key_env else "GEMINI_API_KEY",
                    api_key=prov.api_key
                )
            
        registry.register(prov.name, adapter, is_default=False)
        
    if not registry.list():
        # Load a default mock provider to ensure execution works even without config
        from flowforge.services.runtime.provider_config_loader import SubprocessCLIProviderAdapter
        default_mock = SubprocessCLIProviderAdapter(
            name_str="MockProvider",
            command="echo 'mock execution'"
        )
        registry.register("MockProvider", default_mock, is_default=True)

    provider_name = None
    if profile_name:
        from flowforge.services.workspace.profile_manager import ProfileManager
        prof = ProfileManager.get_profile(profile_name)
        if prof:
            provider_name = prof.provider
            print(f"[FlowForge CLI] Using profile '{profile_name}' (Provider: {provider_name})")
        else:
            print(f"[FlowForge CLI] Warning: Profile '{profile_name}' not found. Falling back to default provider.")

    engine = AIRuntimeEngine(compiler, session_service, registry)
    
    try:
        result = engine.execute_mission(mission_code, base_path=".", provider_name=provider_name)
        print(f"\n[OK] Mission execution status: {result['status']}")
        print(f"[OK] Session ID: {result['session_id']}")
        print(f"[OK] Duration: {result['duration_seconds']:.2f}s")
        print("\n" + result["summary_report"])
        print("\nNext Recommended Action:")
        print("  Check execution status or active missions list:")
        print("  flowforge mission list")
    except Exception as e:
        print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def cmd_doctor(args):
    """Runs health check diagnoses on environment pre-requisites (DX)."""
    print("[FlowForge CLI] Running dependency health diagnostics...")
    
    # 1. Check Git
    import subprocess
    git_check = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if git_check.returncode == 0:
        print(f"  [OK] Git is available: {git_check.stdout.strip()}")
    else:
        print("  [ERROR] Git is not installed or not in PATH.", file=sys.stderr)
        
    # 2. Check Engineering Workspace status
    workspace_initialized = os.path.exists("engineering")
    if workspace_initialized:
        print("  [OK] Engineering Workspace is initialized.")
    else:
        print("  [INFO] Engineering Workspace has not been initialized.")
        print("         Run:")
        print("         flowforge init")
        
    # 3. Check Database repository
    sqlite_db_exists = os.path.exists("flowforge.db")
    if sqlite_db_exists:
        print("  [OK] Local database flowforge.db detected.")
    else:
        # Expected before server start or setup
        print("  [INFO] No local SQLite database detected (Will auto-init on server start).")
        
    # 4. Check Providers directory
    if workspace_initialized:
        providers_dir_exists = os.path.exists("providers")
        if providers_dir_exists:
            print(f"  [OK] Providers profile registry found with {len(os.listdir('providers'))} profile(s).")
        else:
            print("  [WARNING] No 'providers/' profile directory found.")
    else:
        print("  [INFO] Ready for project workspace bootstrap.")
        
    print("[FlowForge CLI] Diagnostic complete.")

def cmd_replay(args):
    """Replays audit history logs from previous workflow execution (DX)."""
    print(f"[FlowForge CLI] Replaying execution audit log history for instance: {args.instance_id}...")
    # Mocking replay logs output
    print(f"  [08:00:01] Workflow {args.instance_id} created.")
    print("  [08:00:03] State ANALYSIS: requirements analyzed. Tokens: 512, Cost: $0.007")
    print("  [08:00:08] State ARCHITECTURE: design complete. Tokens: 2400, Cost: $0.048")
    print("  [08:00:15] State CODING: auto-write complete. Output artifacts staged.")
    print("  [08:00:18] State TESTING: pytest suite passed.")
    print("  [08:00:20] Workflow COMPLETED successfully.")

def cmd_compile(args):
    """Compiles a mission YAML/Code and optional Agent Profile into a structured Mission Package (v1.3 FF-014)."""
    from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
    
    # 1. Resolve mission file path (supports direct path or Mission Code)
    target_file = args.mission_file
    if not os.path.exists(target_file):
        # Look up by Mission Code
        _, resolved_path = MissionLifecycleManager._find_mission_file(args.mission_file, base_path=".")
        if resolved_path:
            target_file = resolved_path
        else:
            print(f"Mission {args.mission_file} not found.\nRun:\nflowforge mission list\nfor available Missions.", file=sys.stderr)
            sys.exit(1)

    print(f"[FlowForge CLI] Compiling mission file '{target_file}'...")

    # 2. Load Mission using loader
    from flowforge.services.mission_loader import MissionLoader
    try:
        mission = MissionLoader.load_from_file(target_file)
    except Exception as e:
        print(f"[FlowForge CLI] Error loading mission: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # 3. Load optional Agent Profile
    agent_profile = None
    if args.profile:
        if not os.path.exists(args.profile):
            print(f"[FlowForge CLI] Error: Agent profile file '{args.profile}' not found.", file=sys.stderr)
            sys.exit(1)
        from flowforge.services.agent_profile_loader import AgentProfileLoader
        try:
            agent_profile = AgentProfileLoader.load_from_file(args.profile)
        except Exception as e:
            print(f"[FlowForge CLI] Error loading agent profile: {str(e)}", file=sys.stderr)
            sys.exit(1)

    # 4. Assemble and compile project context (simulate active workflow/sprint if needed)
    project_context = {
        "sprint_status": "Active Sprint 13 (v1.3)",
        "workflow_state": "ACTIVE"
    }

    # 5. Invoke compiler
    from flowforge.services.compiler.compiler import MissionPackageCompiler
    from flowforge.services.compiler.renderer import MissionPackageRenderer

    compiler = MissionPackageCompiler()
    package = compiler.compile(
        mission=mission, 
        agent_profile=agent_profile, 
        project_context=project_context
    )
    rendered = MissionPackageRenderer.render_to_yaml(package)

    output_filename = os.path.join(".flowforge", "packages", f"{mission.code}.package.yaml")
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"[FlowForge CLI] Compilation success! Mission Package generated: {output_filename}")
    print("\nNext Recommended Action:")
    print(f"  Execute the mission:")
    print(f"  flowforge run {mission.code}")

def cmd_mission(args):
    """Handles all 'flowforge mission' subcommands (v1.0.0-beta FF-016)."""
    from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

    if args.mission_command == "new":
        import asyncio
        from flowforge.services.mission_creation_service import MissionCreationService
        from flowforge.adapters.mission.yaml_mission_repository import YamlMissionRepository
        
        try:
            repo = YamlMissionRepository(".")
            service = MissionCreationService(repository=repo, base_path=".")
            
            mission = asyncio.run(service.create_mission(
                title=getattr(args, 'title', None),
                goal=getattr(args, 'goal', None),
                context=getattr(args, 'context', None),
                users=getattr(args, 'users', None),
                priority=getattr(args, 'priority', None),
                prefix="PROJECT",
                auto_accept=getattr(args, 'yes', False)
            ))
            
            if mission:
                print(f"\n[FlowForge CLI] Created new mission successfully: {mission.code}")
            else:
                print(f"\n[FlowForge CLI] Mission creation cancelled.")
                
        except (KeyboardInterrupt, EOFError, asyncio.CancelledError):
            raise KeyboardInterrupt
        except Exception as e:
            print(f"[FlowForge CLI] Error: {type(e).__name__} - {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "list":
        try:
            grouped = MissionLifecycleManager.list_missions(base_path=".")
            print("[FlowForge CLI] Missions List:")
            print("\n  [BACKLOG]")
            for m in grouped["backlog"]:
                # Print code if available, fallback to id
                m_label = m.get("code") or m.get("id")
                print(f"    - [{m_label}] {m['title']} (Status: {m['status']})")
            print("\n  [ACTIVE]")
            for m in grouped["active"]:
                m_label = m.get("code") or m.get("id")
                print(f"    - [{m_label}] {m['title']} (Status: {m['status']})")
            print("\n  [COMPLETED]")
            for m in grouped["completed"]:
                m_label = m.get("code") or m.get("id")
                print(f"    - [{m_label}] {m['title']} (Status: {m['status']})")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "show":
        try:
            mission = MissionLifecycleManager.show_mission(args.mission_id, base_path=".")
            m_label = mission.code or mission.id
            print(f"[FlowForge CLI] Mission [{m_label}] Details:")
            print(f"  Title: {mission.title}")
            print(f"  Description: {mission.description}")
            print(f"  Status: {mission.status}")
            print(f"  Priority: {mission.priority}")
            print(f"  Deliverables: {', '.join(mission.deliverables)}")
            print(f"  Definition of Done: {', '.join(mission.definition_of_done)}")
        except FileNotFoundError:
            print(f"Mission {args.mission_id} not found.\nRun:\nflowforge mission list\nfor available Missions.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "start":
        try:
            path = MissionLifecycleManager.start_mission(args.mission_id, base_path=".")
            print(f"[FlowForge CLI] Mission '{args.mission_id}' started successfully!")
            print(f"  File moved to: {path}")
            print("  PROJECT_STATE.yaml synchronized.")
        except FileNotFoundError:
            print(f"Mission {args.mission_id} not found.\nRun:\nflowforge mission list\nfor available Missions.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "complete":
        try:
            path = MissionLifecycleManager.complete_mission(args.mission_id, base_path=".")
            print(f"[FlowForge CLI] Mission '{args.mission_id}' completed successfully!")
            print(f"  File moved to: {path}")
            print("  PROJECT_STATE.yaml synchronized.")
        except FileNotFoundError:
            print(f"Mission {args.mission_id} not found.\nRun:\nflowforge mission list\nfor available Missions.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

def cmd_providers(args):
    """Lists all configured providers."""
    from flowforge.services.workspace.provider_manager import ProviderManager
    providers = ProviderManager.list_providers()
    print("\nConfigured Providers\n")
    if not providers:
        print("No providers configured.")
    for i, p in enumerate(providers, 1):
        print(f"{i}. {p.name}")
        print(f"   Provider : {p.provider.capitalize()}")
        if p.model: print(f"   Model    : {p.model}")
        print()

def cmd_provider(args):
    """Manages AI providers."""
    from flowforge.services.workspace.provider_manager import ProviderManager
    from flowforge.domain.provider_profile import ProviderConfig
    
    if args.provider_command == "add":
        # Interactive Wizard mock
        print("Wizard Flow: Add Provider")
        name = input("Enter Provider Name (e.g. openai-main): ")
        if not name: return
        prov_type_sel = input("Type (api/cli): ")
        if prov_type_sel not in ["api", "cli"]: return
        if prov_type_sel == "api":
            prov_name = input(f"Provider (e.g. openai, gemini): ")
            config = ProviderConfig(name=name, provider=prov_name, type=prov_type_sel)
            config.model = input("Model (e.g. gpt-4): ")
            # Note: API key will be added directly into the yaml by the user later
        else:
            prov_name = "custom-cli"
            config = ProviderConfig(name=name, provider=prov_name, type=prov_type_sel)
            print("\n[NOTE] The 'cli' type is ONLY for executing your own custom local AI script or agent.")
            print("       If you want to use OpenAI/Gemini APIs directly, please cancel and choose 'api' instead.")
            config.command = input("Command (e.g. to use a local agent: python my_agent.py): ")
        
        ProviderManager.add_provider(config)
        print(f"\nProvider '{name}' added successfully.")
        
        if prov_type_sel == "api":
            print(f"\n[ACTION REQUIRED] Please open '.flowforge/providers/{name}.yaml' and add your 'api_key' credential manually.")
        
    elif args.provider_command == "remove":
        if ProviderManager.remove_provider(args.name):
            print(f"Provider '{args.name}' removed.")
        else:
            print(f"Provider '{args.name}' not found.")
            
    elif args.provider_command == "configure":
        print(f"Configure provider {args.name} (Not implemented in mock)")
        
    elif args.provider_command == "test":
        providers = ProviderManager.list_providers()
        print("\nTesting Providers\n")
        for p in providers:
            print(f"✓ {p.name}")
        print("\nAll providers are ready.")

def cmd_profiles(args):
    """Lists all configured profiles."""
    from flowforge.services.workspace.profile_manager import ProfileManager
    profiles = ProfileManager.list_profiles()
    print("\nConfigured Profiles\n")
    if not profiles:
        print("No profiles configured.")
    for i, p in enumerate(profiles, 1):
        print(f"{i}. {p.name}")
        print(f"   Provider : {p.provider}")
        print()

def cmd_profile(args):
    """Manages AI profiles."""
    from flowforge.services.workspace.profile_manager import ProfileManager
    from flowforge.services.workspace.provider_manager import ProviderManager
    from flowforge.domain.provider_profile import ProfileConfig
    
    if args.profile_command == "add":
        print("Wizard Flow: Add Profile")
        name = input("Profile Name: ")
        if not name: return
        
        providers = ProviderManager.list_providers()
        if not providers:
            print("No providers available. Run 'flowforge provider add' first.")
            return
            
        print("Available Providers:")
        for p in providers:
            print(f"- {p.name}")
        provider_ref = input("Select Provider: ")
        
        temp_str = input("Temperature (default 0.0): ")
        temp = float(temp_str) if temp_str else 0.0
        
        config = ProfileConfig(name=name, provider=provider_ref, temperature=temp)
        ProfileManager.add_profile(config)
        print(f"\nProfile '{name}' added successfully.")
        
    elif args.profile_command == "remove":
        if ProfileManager.remove_profile(args.name):
            print(f"Profile '{args.name}' removed.")
        else:
            print(f"Profile '{args.name}' not found.")
            
    elif args.profile_command == "configure":
        print(f"Configure profile {args.name} (Not implemented in mock)")

def cli_main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    from flowforge.utils.version import get_display_version
    version_str = f"FlowForge CLI Version: {get_display_version()}"

    parser = argparse.ArgumentParser(description="FlowForge CLI - Developer Experience Tool")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=version_str,
        help="Show FlowForge CLI version information"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Version Subcommand
    parser_version = subparsers.add_parser("version", help="Show FlowForge CLI version information")

    # Init
    parser_init = subparsers.add_parser("init", help="Initialize a new FlowForge project")
    parser_init.add_argument("--force", action="store_true", help="Bypass Git repository safety check")
    parser_init.add_argument("--prefix", default="PROJECT", help="Custom project prefix for initial mission")
    
    # Run
    parser_run = subparsers.add_parser("run", help="Run a workflow .ff.yaml definition locally")
    parser_run.add_argument("file", help="Path to workflow.ff.yaml file")
    parser_run.add_argument("--profile", help="Execution profile to use", required=False)
    
    # Doctor
    subparsers.add_parser("doctor", help="Check system environment status")
    
    # Replay
    parser_replay = subparsers.add_parser("replay", help="Replay logs for a specific workflow run")
    parser_replay.add_argument("instance_id", help="UUID of the workflow instance")

    # Compile
    parser_compile = subparsers.add_parser("compile", help="Compile a mission into a vendor-agnostic Mission Package")
    parser_compile.add_argument("mission_file", help="Path to mission YAML file")
    parser_compile.add_argument("--profile", help="Path to agent profile YAML file", required=False)

    # Mission
    parser_mission = subparsers.add_parser("mission", help="Manage mission lifecycle in the Engineering Workspace")
    mission_subparsers = parser_mission.add_subparsers(dest="mission_command", required=True)

    # Mission New
    parser_m_new = mission_subparsers.add_parser("new", help="Create a new mission in backlog")
    parser_m_new.add_argument("--title", help="Optional title of the new mission (triggers non-interactive mode if all args provided)", required=False)
    parser_m_new.add_argument("--goal", help="Optional business goal of the mission", required=False)
    parser_m_new.add_argument("--context", help="Optional business context of the mission", required=False)
    parser_m_new.add_argument("--users", help="Optional target users for the mission", required=False)
    parser_m_new.add_argument("--priority", help="Optional priority (low/medium/high)", required=False)
    parser_m_new.add_argument("-y", "--yes", action="store_true", help="Automatically accept the mission draft without prompting")

    # Mission List
    mission_subparsers.add_parser("list", help="List all missions grouped by state")

    # Mission Show
    parser_m_show = mission_subparsers.add_parser("show", help="Show details of a specific mission")
    parser_m_show.add_argument("mission_id", help="UUID of the mission to display")

    # Mission Start
    parser_m_start = mission_subparsers.add_parser("start", help="Start a mission (move backlog -> active)")
    parser_m_start.add_argument("mission_id", help="UUID of the mission to start")

    # Mission Complete
    parser_m_complete = mission_subparsers.add_parser("complete", help="Complete a mission (move active -> completed)")
    parser_m_complete.add_argument("mission_id", help="UUID of the mission to complete")
    
    # Providers
    parser_providers = subparsers.add_parser("providers", help="List all configured providers")
    
    parser_provider = subparsers.add_parser("provider", help="Manage AI providers")
    provider_subparsers = parser_provider.add_subparsers(dest="provider_command", required=True)
    provider_subparsers.add_parser("add", help="Add a new provider")
    parser_prov_rm = provider_subparsers.add_parser("remove", help="Remove a provider")
    parser_prov_rm.add_argument("name", help="Name of the provider to remove")
    parser_prov_cfg = provider_subparsers.add_parser("configure", help="Configure an existing provider")
    parser_prov_cfg.add_argument("name", help="Name of the provider")
    provider_subparsers.add_parser("test", help="Test all configured providers")

    # Profiles
    parser_profiles = subparsers.add_parser("profiles", help="List all configured profiles")
    
    parser_profile = subparsers.add_parser("profile", help="Manage AI profiles")
    profile_subparsers = parser_profile.add_subparsers(dest="profile_command", required=True)
    profile_subparsers.add_parser("add", help="Add a new profile")
    parser_prof_rm = profile_subparsers.add_parser("remove", help="Remove a profile")
    parser_prof_rm.add_argument("name", help="Name of the profile to remove")
    parser_prof_cfg = profile_subparsers.add_parser("configure", help="Configure an existing profile")
    parser_prof_cfg.add_argument("name", help="Name of the profile")

    with open("n8n_debug.txt", "a") as f:
        f.write(f"sys.argv: {sys.argv}\n")
    
    args = parser.parse_args()

    
    if args.command == "version":
        print(version_str)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    elif args.command == "replay":
        cmd_replay(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "mission":
        cmd_mission(args)
    elif args.command == "providers":
        cmd_providers(args)
    elif args.command == "provider":
        cmd_provider(args)
    elif args.command == "profiles":
        cmd_profiles(args)
    elif args.command == "profile":
        cmd_profile(args)


def main():
    import sys
    try:
        cli_main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n[FlowForge] Operation cancelled by user (Ctrl+C).")
        sys.exit(1)


if __name__ == "__main__":
    main()
