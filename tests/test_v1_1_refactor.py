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

    # Invalid event on current state should raise error
    with pytest.raises(InvalidTransitionError):
        engine.transition(instance, "APPROVE")

# 2. Test YAML Loader and .ff.yaml extension
def test_yaml_loader_and_ff_extension(tmp_path):
    yaml_content = """
name: "AI Coder Workflow"
version: "1.1.0"
initial_state: "ANALYSIS"
states:
  ANALYSIS:
    name: "Requirements Analysis"
    require_human: false
  ARCHITECTURE:
    name: "System Architecture"
    require_human: true
transitions:
  - from: "ANALYSIS", event: "SUCCESS", to: "ARCHITECTURE"
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
    resolver = CapabilityResolver()
    
    mock_claude = MagicMock()
    mock_codex = MagicMock()
    mock_gemini = MagicMock()
    
    # Only register codex and gemini
    resolver.register_provider("codex", mock_codex)
    resolver.register_provider("gemini", mock_gemini)
    
    # Resolve coding capability: fallback coding list = ["codex", "gpt", "qwen"] -> codex is available!
    provider = resolver.resolve_best_provider("coding")
    assert provider == mock_codex

    # Resolve architecture capability: fallback list = ["claude", "gpt", "gemini"]
    # claude and gpt are NOT registered. gemini IS registered -> resolved provider should fallback to gemini!
    provider = resolver.resolve_best_provider("architecture")
    assert provider == mock_gemini

# 4. Test Prompt Pipeline
def test_prompt_pipeline(tmp_path):
    # Template utilizing memory, artifacts, git, and file workspace context
    template = (
        "Memory Context:\n{memory_context}\n\n"
        "Artifact Code:\n{artifact_patch_diff}\n\n"
        "Workspace File:\n{file_utils_py}\n\n"
        "Git status:\n{git_diff}\n\n"
        "Instructions: Fix {bug}"
    )
    
    # Create workspace file dummy
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
    
    # Create markdown type artifact (auto-detected)
    art1 = manager.create_artifact(instance_id, "doc.md", "doc.md", "# Document")
    assert art1.artifact_type == "MARKDOWN"

    # Create png type artifact (custom specified)
    art2 = manager.create_artifact(instance_id, "img.png", "img.png", "binary_data", artifact_type="PNG")
    assert art2.artifact_type == "PNG"

    # Create patch type artifact (auto-detected)
    art3 = manager.create_artifact(instance_id, "code.patch", "code.patch", "@@ -1,3 +1,3 @@")
    assert art3.artifact_type == "PATCH"

# 6. Test Lesson Learned Memory Engine
@pytest.mark.asyncio
async def test_lesson_learned_memory_engine(tmp_path):
    store = LessonLearnedStore(memory_dir=str(tmp_path))
    
    # Add lessons learned
    store.add_lesson("coder-wf", "Always check index bounds in loops")
    store.add_lesson("coder-wf", "Close DB sessions on exception")
    
    assert len(store.get_lessons("coder-wf")) == 2
    assert "Always check index bounds in loops" in store.get_lessons("coder-wf")

    # Persist to disk
    await store.persist()
    
    # Verify JSON file structure
    lessons_json = tmp_path / "lessons.json"
    assert os.path.exists(lessons_json)
    
    # Load back in another instance
    new_store = LessonLearnedStore(memory_dir=str(tmp_path))
    await new_store.load()
    
    assert len(new_store.get_lessons("coder-wf")) == 2
    assert "Close DB sessions on exception" in new_store.get_lessons("coder-wf")

# 7. Test Plugin Auto-Discovery
def test_plugin_auto_discovery():
    from flowforge.domain.plugin_manager import PluginManager
    manager = PluginManager()
    manager.discover_and_register_plugins()
    assert len(manager.plugins) == 0  # No plugins registered in test env

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
    
    # 1. Clone sandbox
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
    
    mock_claude = MagicMock()
    mock_gemini = MagicMock()
    mock_qwen = MagicMock()
    
    engine.register_provider("claude", mock_claude)
    engine.register_provider("gemini", mock_gemini)
    engine.register_provider("qwen", mock_qwen)
    
    # cost-first coding fallback is ["qwen", "codex", "gpt"] -> qwen is registered!
    provider1 = engine.resolve_provider_by_policy("coding")
    assert provider1 == mock_qwen
    
    # Switch to quality-first
    engine.strategy = "quality-first"
    # quality-first coding fallback is ["claude", "codex", "gpt"] -> claude is registered!
    provider2 = engine.resolve_provider_by_policy("coding")
    assert provider2 == mock_claude

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
        
        # Modify file inside local workspace adapter
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
