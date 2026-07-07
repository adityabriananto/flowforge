import sys
import os
import uuid
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig, Job
from flowforge.domain.engine import StateMachine, InvalidTransitionError
from flowforge.domain.yaml_loader import load_workflow_from_yaml, load_workflow_from_file
from flowforge.domain.capability_resolver import CapabilityResolver
from flowforge.domain.prompt_builder import PromptPipeline
from flowforge.domain.artifact_manager import ArtifactManager
from flowforge.domain.memory import Memory, LessonLearnedStore
from flowforge.ports.execution_provider import ExecutionProvider
from flowforge.adapters.execution.cli_provider import CliExecutionProvider
from flowforge.adapters.execution.api_provider import ApiExecutionProvider
from flowforge.domain.provider_config import CliProviderConfig
from flowforge.domain.workspace_sandbox import WorkspaceSandbox
from flowforge.adapters.worker.subprocess_runtime import SubprocessWorkerRuntime

# Import v1.2 new Clean Architecture components
from flowforge.services.resolver.policy_engine import CapabilityPolicyEngine
from flowforge.adapters.workspace.local_workspace import LocalWorkspace
from flowforge.services.resolver.provider_registry import ProviderRegistry
from flowforge.services.prompt.prompt_pipeline import (
    PromptPipeline as ServicePromptPipeline,
    WorkspaceLoaderStage,
    MemoryLoaderStage,
    ArtifactLoaderStage,
    GitLoaderStage
)
from flowforge.entrypoints.cli.main import cmd_init, cmd_run, cmd_doctor, cmd_replay

# 1. Test Transition Table
def test_transition_table_execution():
    states = {
        "ANALYSIS": StateConfig(name="ANALYSIS"),
        "ARCHITECTURE": StateConfig(name="ARCHITECTURE"),
        "IMPLEMENTATION": StateConfig(name="IMPLEMENTATION")
    }
    transitions = {
        ("ANALYSIS", "SUCCESS"): "ARCHITECTURE",
        ("ARCHITECTURE", "APPROVE"): "IMPLEMENTATION"
    }
    workflow = Workflow(
        id=uuid.uuid4(),
        name="Table Workflow",
        version="1.1.0",
        initial_state="ANALYSIS",
        states=states,
        transitions=transitions
    )
    
    engine = StateMachine(workflow)
    instance = WorkflowInstance(id=uuid.uuid4(), workflow_id=workflow.id, current_state="ANALYSIS")
    
    # Run valid transitions
    event1 = engine.transition(instance, "SUCCESS")
    assert instance.current_state == "ARCHITECTURE"
    assert event1.payload["from_state"] == "ANALYSIS"
    assert event1.payload["to_state"] == "ARCHITECTURE"
    
    event2 = engine.transition(instance, "APPROVE")
    assert instance.current_state == "IMPLEMENTATION"

    with pytest.raises(InvalidTransitionError):
        engine.transition(instance, "APPROVE")

# 2. Test YAML Loader and .ff.yaml extension
def test_yaml_loader_and_ff_extension(tmp_path):
    yaml_content = """
name: "AI Coder Workflow"
version: "1.1.0"
initial_state: "ANALYSIS"
roles:
  architect:
    capability: architecture
    policy: quality-first
states:
  ANALYSIS:
    name: "Requirements Analysis"
    require_human: false
transitions:
  - { from: "ANALYSIS", event: "SUCCESS", to: "ARCHITECTURE" }
"""
    # Test load from yaml content
    workflow = load_workflow_from_yaml(yaml_content)
    assert workflow.name == "AI Coder Workflow"
    assert workflow.initial_state == "ANALYSIS"
    assert workflow.transitions[("ANALYSIS", "SUCCESS")] == "ARCHITECTURE"

    # Save with invalid extension and test error raise
    invalid_file = tmp_path / "workflow.yaml"
    invalid_file.write_text(yaml_content)
    with pytest.raises(ValueError) as exc:
        load_workflow_from_file(str(invalid_file))
    assert "must strictly end with '.ff.yaml'" in str(exc.value)

    # Save with valid .ff.yaml extension and test successful load
    valid_file = tmp_path / "workflow.ff.yaml"
    valid_file.write_text(yaml_content)
    loaded_wf = load_workflow_from_file(str(valid_file))
    assert loaded_wf.name == "AI Coder Workflow"
    assert loaded_wf.transitions[("ANALYSIS", "SUCCESS")] == "ARCHITECTURE"

# 3. Test Dynamic Capability Fallback List Resolver
def test_dynamic_capability_resolver():
    # Capability map must be explicitly provided — core has zero hardcoded vendor names
    resolver = CapabilityResolver(custom_mapping={
        "coding": ["provider_fast", "provider_quality"],
        "architecture": ["provider_quality", "provider_fast"],
    })
    
    mock_fast = MagicMock()
    mock_quality = MagicMock()
    
    resolver.register_provider("provider_fast", mock_fast)
    resolver.register_provider("provider_quality", mock_quality)
    
    provider = resolver.resolve_best_provider("coding")
    assert provider == mock_fast

    provider = resolver.resolve_best_provider("architecture")
    assert provider == mock_quality

# 4. Test Prompt Pipeline
def test_prompt_pipeline(tmp_path):
    template = (
        "Memory Context:\n{memory_context}\n\n"
        "Artifact Code:\n{artifact_patch_diff}\n\n"
        "Workspace File:\n{file_utils_py}\n\n"
        "Git status:\n{git_diff}\n\n"
        "Instructions: Fix {bug}"
    )
    
    workspace_file = tmp_path / "utils.py"
    workspace_file.write_text("def run(): pass")

    pipeline = PromptPipeline(template)
    compiled_prompt = (
        pipeline.load_memory(["Always wrap SQL with quotes", "Never delete main.py"])
        .load_artifact("patch.diff", "diff -u main.py")
        .load_workspace_file(str(workspace_file))
        .load_git_diff("git status clean")
        .build({"bug": "syntax error"})
    )

    assert "- Always wrap SQL with quotes" in compiled_prompt
    assert "- Never delete main.py" in compiled_prompt
    assert "diff -u main.py" in compiled_prompt
    assert "def run(): pass" in compiled_prompt
    assert "git status clean" in compiled_prompt
    assert "Instructions: Fix syntax error" in compiled_prompt

# 5. Test Extended Rich Artifact Manager
def test_extended_artifact_manager(tmp_path):
    manager = ArtifactManager(storage_dir=str(tmp_path))
    instance_id = uuid.uuid4()
    
    art1 = manager.create_artifact(instance_id, "doc.md", "doc.md", "# Document")
    assert art1.artifact_type == "MARKDOWN"

    art2 = manager.create_artifact(instance_id, "img.png", "img.png", "binary_data", artifact_type="PNG")
    assert art2.artifact_type == "PNG"

    art3 = manager.create_artifact(instance_id, "code.patch", "code.patch", "@@ -1,3 +1,3 @@")
    assert art3.artifact_type == "PATCH"

# 6. Test Lesson Learned Memory Engine
@pytest.mark.asyncio
async def test_lesson_learned_memory_engine(tmp_path):
    store = LessonLearnedStore(memory_dir=str(tmp_path))
    
    store.add_lesson("coder-wf", "Always check index bounds in loops")
    store.add_lesson("coder-wf", "Close DB sessions on exception")
    
    assert len(store.get_lessons("coder-wf")) == 2
    assert "Always check index bounds in loops" in store.get_lessons("coder-wf")

    await store.persist()
    
    lessons_json = tmp_path / "lessons.json"
    assert os.path.exists(lessons_json)
    
    new_store = LessonLearnedStore(memory_dir=str(tmp_path))
    await new_store.load()
    
    assert len(new_store.get_lessons("coder-wf")) == 2
    assert "Close DB sessions on exception" in new_store.get_lessons("coder-wf")

# 7. Test Plugin Auto-Discovery
def test_plugin_auto_discovery():
    from flowforge.domain.plugin_manager import PluginManager
    manager = PluginManager()
    manager.discover_and_register_plugins()
    assert len(manager.plugins) == 0

# 8. Test Execution Provider (Challenge #10 & #2)
@pytest.mark.asyncio
async def test_execution_providers():
    config = CliProviderConfig(executable="fake-cli", command="run", args=["--dry-run"])
    cli_provider = CliExecutionProvider(config)
    
    res = await cli_provider.execute("Optimize loops", {"artifacts": ["main.py"]})
    assert res["status"] in ["SUCCESS", "FAILED"]
    assert res["artifacts"] == ["main.py"]
    assert "metrics" in res
    
    mock_connector = AsyncMock()
    mock_connector.generate_text.return_value = "optimized_code"
    api_provider = ApiExecutionProvider(mock_connector)
    
    api_res = await api_provider.execute("Refactor function", {"artifacts": ["utils.py"]})
    assert api_res["status"] == "SUCCESS"
    assert api_res["content"] == "optimized_code"
    assert api_res["artifacts"] == ["utils.py"]

# 9. Test Workspace Sandbox & Git branching (Challenge #3, #6 & #7)
@pytest.mark.asyncio
async def test_workspace_sandbox(tmp_path):
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.email", "test@user.com"], cwd=str(tmp_path), check=True)
    
    start_file = tmp_path / "hello.txt"
    start_file.write_text("initial")
    subprocess.run(["git", "add", "hello.txt"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=str(tmp_path), check=True)
    
    sandbox = WorkspaceSandbox(str(tmp_path))
    
    sandbox_path = await sandbox.clone_sandbox()
    assert os.path.exists(sandbox_path)
    assert os.path.exists(os.path.join(sandbox_path, "hello.txt"))
    
    try:
        assert await sandbox.verify_git_diff(sandbox_path) == "NO_CHANGE"
        mod_file = os.path.join(sandbox_path, "hello.txt")
        with open(mod_file, "w") as f:
            f.write("modified")
            
        assert await sandbox.verify_git_diff(sandbox_path) == "SUCCESS"
        
        job_id = "9999"
        branch_name = await sandbox.create_auto_commit_branch(sandbox_path, job_id)
        assert branch_name == "flowforge/JOB-9999"
        
        branch_res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=sandbox_path,
            capture_output=True,
            text=True,
            check=True
        )
        assert branch_res.stdout.strip() == "flowforge/JOB-9999"
    finally:
        sandbox.cleanup(sandbox_path)

# 10. Test Subprocess Runtime JSON Parsing (Challenge #9)
@pytest.mark.asyncio
async def test_subprocess_runtime_json_output(tmp_path):
    runtime = SubprocessWorkerRuntime()
    job = Job(id=uuid.uuid4(), instance_id=uuid.uuid4(), state_name="CODING", status="PENDING")
    
    script_content = """
import json
with open("result.json", "w") as f:
    json.dump({
        "status": "FAILED",
        "error": "syntax error on line 4",
        "artifacts": []
    }, f)
"""
    script_file = tmp_path / "run_cli.py"
    script_file.write_text(script_content)
    
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        updated_job = await runtime.execute_job(job, str(script_file))
        assert updated_job.status == "FAILED"
        assert "[Structured error]" in updated_job.stderr
    finally:
        os.chdir(old_cwd)

# 11. Test Capability Policy Engine (v1.2 Priority 3 / Challenge #2)
def test_capability_policy_engine():
    engine = CapabilityPolicyEngine(policy_strategy="cost-first")
    
    mock_provider_a = MagicMock()
    mock_provider_b = MagicMock()
    mock_provider_c = MagicMock()
    
    engine.register_provider("provider_a", mock_provider_a)
    engine.register_provider("provider_b", mock_provider_b)
    engine.register_provider("provider_c", mock_provider_c)
    
    # Set policy rules explicitly (no hardcoded vendor names in engine)
    engine.capability_policy["cost-first"] = {
        "coding": ["provider_c", "provider_b", "provider_a"],
    }
    engine.capability_policy["quality-first"] = {
        "coding": ["provider_a", "provider_b", "provider_c"],
    }
    
    provider1 = engine.resolve_provider_by_policy("coding")
    assert provider1 == mock_provider_c
    
    engine.strategy = "quality-first"
    provider2 = engine.resolve_provider_by_policy("coding")
    assert provider2 == mock_provider_a

# 12. Test LocalWorkspace Port & Adapter (v1.2 Challenge #6)
@pytest.mark.asyncio
async def test_local_workspace_adapter(tmp_path):
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.email", "test@user.com"], cwd=str(tmp_path), check=True)
    
    start_file = tmp_path / "hello.txt"
    start_file.write_text("initial")
    subprocess.run(["git", "add", "hello.txt"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=str(tmp_path), check=True)
    
    workspace = LocalWorkspace(str(tmp_path), job_id="1234")
    sandbox_path = await workspace.setup()
    assert os.path.exists(sandbox_path)
    
    try:
        assert await workspace.check_diff() == "NO_CHANGE"
        
        mod_file = os.path.join(sandbox_path, "hello.txt")
        with open(mod_file, "w") as f:
            f.write("modified-via-adapter")
            
        assert await workspace.check_diff() == "SUCCESS"
        
        branch_name = await workspace.commit_changes("feat: committed via local workspace adapter")
        assert branch_name == "flowforge/JOB-1234"
        
        branch_res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=sandbox_path,
            capture_output=True,
            text=True,
            check=True
        )
        assert branch_res.stdout.strip() == "flowforge/JOB-1234"
    finally:
        workspace.cleanup()

# 13. Test Dynamic YAML Provider Registry (Challenge #16)
def test_yaml_provider_registry(tmp_path):
    # Setup dummy provider yaml configurations
    os.makedirs(tmp_path / "providers", exist_ok=True)
    
    claude_yaml = """name: "claude"
capabilities:
  reasoning: 95
  coding: 85
cost: "high"
speed: "medium"
"""
    gemini_yaml = """name: "gemini"
capabilities:
  reasoning: 80
  coding: 90
cost: "low"
speed: "fast"
"""
    with open(tmp_path / "providers" / "claude.yaml", "w", encoding="utf-8") as f:
        f.write(claude_yaml)
    with open(tmp_path / "providers" / "gemini.yaml", "w", encoding="utf-8") as f:
        f.write(gemini_yaml)
        
    registry = ProviderRegistry(providers_dir=str(tmp_path / "providers"))
    
    mock_claude = MagicMock()
    mock_gemini = MagicMock()
    registry.register_connector("claude", mock_claude)
    registry.register_connector("gemini", mock_gemini)
    
    # quality-first reasoning resolve should favor claude (95 vs 80)
    best_quality = registry.resolve_by_policy("reasoning", strategy="quality-first")
    assert best_quality == mock_claude
    
    # cost-first coding resolve should favor gemini due to cost weight modifier (low cost vs high cost)
    best_cost = registry.resolve_by_policy("coding", strategy="cost-first")
    assert best_cost == mock_gemini

# 14. Test Middleware-based Prompt Pipeline (Challenge #17)
@pytest.mark.asyncio
async def test_middleware_prompt_pipeline(tmp_path):
    template = "Instruction: {instructions}. Code snippet: {file_run_py}"
    pipeline = ServicePromptPipeline(template)
    
    # Create workspace file dummy
    workspace_file = tmp_path / "run.py"
    workspace_file.write_text("print('hello')")
    
    pipeline.add_stage(WorkspaceLoaderStage(str(workspace_file)))
    
    result = await pipeline.execute_pipeline({"instructions": "Analyze loops"})
    assert "Analyze loops" in result
    assert "print('hello')" in result

# 15. Test CLI Subcommands DX Execution
def test_cli_subcommands(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        # Mock argparse args
        class Args:
            pass
            
        args_init = Args()
        cmd_init(args_init)
        
        assert os.path.exists("workflow.ff.yaml")
        assert os.path.exists("providers/claude.yaml")
        assert os.path.exists("providers/gemini.yaml")
        
        args_doctor = Args()
        cmd_doctor(args_doctor)
        
        args_replay = Args()
        args_replay.instance_id = "test-uuid-1234"
        cmd_replay(args_replay)
        
        # Test cmd_run locally
        args_run = Args()
        args_run.file = "workflow.ff.yaml"
        cmd_run(args_run)
        
    finally:
        os.chdir(old_cwd)

# 16. Test Dogfooding Self-CI/CD FFWL Loading (Challenge #4)
def test_dogfooding_cicd_workflow():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ffwl_path = os.path.join(root_dir, "workflow.ff.yaml")
    workflow = load_workflow_from_file(ffwl_path)
    assert workflow.name == "FlowForge Self-CI/CD Workflow"
    assert workflow.initial_state == "ANALYSIS"
    assert workflow.transitions[("ANALYSIS", "SUCCESS")] == "TESTING"
    assert workflow.transitions[("TESTING", "SUCCESS")] == "AUDIT"
