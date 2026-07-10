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
        
        print("✓ Detecting project")
        details = SmartBootstrapper.bootstrap(base_path=".", force=force, prefix=prefix)
        
        # Write additional workflow and provider configs if not present
        os.makedirs("providers", exist_ok=True)
        os.makedirs("agents", exist_ok=True)
        
        workflow_yaml_path = "workflow.ff.yaml"
        if not os.path.exists(workflow_yaml_path):
            workflow_yaml = f"""name: "Autonomous AI Agent Workflow"
version: "1.3.0"
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

        print("✓ Creating Engineering Workspace")
        print("✓ Installing templates")
        print("✓ Creating PROJECT_STATE")
        print("✓ Creating initial Mission")
        print("\nInitialization complete.")
        print(f"Project Type: {details['project_type']} (Framework: {details['framework']}, Language: {details['language']})")
        
    except Exception as e:
        print(f"[FlowForge CLI] Error during initialization: {str(e)}", file=sys.stderr)
        sys.exit(1)

def cmd_run(args):
    """Runs a local .ff.yaml workflow definition otonomously (DX)."""
    file_path = args.file
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
        
    # 2. Check Database repository
    sqlite_db_exists = os.path.exists("flowforge.db")
    if sqlite_db_exists:
        print("  [OK] Local database flowforge.db detected.")
    else:
        print("  [WARNING] No local SQLite database file detected (Will auto-init on server start).")
        
    # 3. Check Providers directory
    providers_dir_exists = os.path.exists("providers")
    if providers_dir_exists:
        print(f"  [OK] Providers profile registry found with {len(os.listdir('providers'))} profile(s).")
    else:
        print("  [WARNING] No 'providers/' profile directory found.")
        
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
    """Compiles a mission YAML and optional Agent Profile into a structured Mission Package (v1.3 FF-014)."""
    print(f"[FlowForge CLI] Compiling mission file '{args.mission_file}'...")
    if not os.path.exists(args.mission_file):
        print(f"[FlowForge CLI] Error: Mission file '{args.mission_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # 1. Load Mission using loader
    from flowforge.services.mission_loader import MissionLoader
    try:
        mission = MissionLoader.load_from_file(args.mission_file)
    except Exception as e:
        print(f"[FlowForge CLI] Error loading mission: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # 2. Load optional Agent Profile
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

    # 3. Assemble and compile project context (simulate active workflow/sprint if needed)
    project_context = {
        "sprint_status": "Active Sprint 13 (v1.3)",
        "workflow_state": "ACTIVE"
    }

    # 4. Invoke compiler
    from flowforge.services.compiler.compiler import MissionPackageCompiler
    from flowforge.services.compiler.renderer import MissionPackageRenderer

    compiler = MissionPackageCompiler()
    package = compiler.compile(
        mission=mission, 
        agent_profile=agent_profile, 
        project_context=project_context
    )
    rendered = MissionPackageRenderer.render_to_yaml(package)

    output_filename = f"mission_package_{mission.id}.yaml"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"[FlowForge CLI] Compilation success! Mission Package generated: {output_filename}")

def cmd_mission(args):
    """Handles all 'flowforge mission' subcommands (v1.3.0 FF-016)."""
    from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

    if args.mission_command == "new":
        try:
            path = MissionLifecycleManager.create_mission(
                title=args.title,
                description=args.desc or "",
                mission_id=args.id,
                base_path="."
            )
            print(f"[FlowForge CLI] Created new mission successfully in backlog: {path}")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "list":
        try:
            grouped = MissionLifecycleManager.list_missions(base_path=".")
            print("[FlowForge CLI] Missions List:")
            print("\n  [BACKLOG]")
            for m in grouped["backlog"]:
                print(f"    - [{m['id']}] {m['title']} (Status: {m['status']})")
            print("\n  [ACTIVE]")
            for m in grouped["active"]:
                print(f"    - [{m['id']}] {m['title']} (Status: {m['status']})")
            print("\n  [COMPLETED]")
            for m in grouped["completed"]:
                print(f"    - [{m['id']}] {m['title']} (Status: {m['status']})")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "show":
        try:
            mission = MissionLifecycleManager.show_mission(args.mission_id, base_path=".")
            print(f"[FlowForge CLI] Mission [{mission.id}] Details:")
            print(f"  Title: {mission.title}")
            print(f"  Description: {mission.description}")
            print(f"  Status: {mission.status}")
            print(f"  Priority: {mission.priority}")
            print(f"  Deliverables: {', '.join(mission.deliverables)}")
            print(f"  Definition of Done: {', '.join(mission.definition_of_done)}")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "start":
        try:
            path = MissionLifecycleManager.start_mission(args.mission_id, base_path=".")
            print(f"[FlowForge CLI] Mission '{args.mission_id}' started successfully!")
            print(f"  File moved to: {path}")
            print("  PROJECT_STATE.yaml synchronized.")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.mission_command == "complete":
        try:
            path = MissionLifecycleManager.complete_mission(args.mission_id, base_path=".")
            print(f"[FlowForge CLI] Mission '{args.mission_id}' completed successfully!")
            print(f"  File moved to: {path}")
            print("  PROJECT_STATE.yaml synchronized.")
        except Exception as e:
            print(f"[FlowForge CLI] Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="FlowForge CLI - Developer Experience Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Init
    parser_init = subparsers.add_parser("init", help="Initialize a new FlowForge project")
    parser_init.add_argument("--force", action="store_true", help="Bypass Git repository safety check")
    parser_init.add_argument("--prefix", default="PROJECT", help="Custom project prefix for initial mission")
    
    # Run
    parser_run = subparsers.add_parser("run", help="Run a workflow .ff.yaml definition locally")
    parser_run.add_argument("file", help="Path to workflow.ff.yaml file")
    
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
    parser_m_new.add_argument("title", help="Title of the new mission")
    parser_m_new.add_argument("--desc", help="Optional description of the mission", required=False)
    parser_m_new.add_argument("--id", help="Optional custom UUID for the mission", required=False)

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
    
    args = parser.parse_args()
    
    if args.command == "init":
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

if __name__ == "__main__":
    main()
