import sys
import os
import uuid
import pytest
from unittest.mock import MagicMock

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig
from flowforge.domain.engine import StateMachine, InvalidTransitionError
from flowforge.domain.yaml_loader import load_workflow_from_yaml, load_workflow_from_file
from flowforge.domain.capability_resolver import CapabilityResolver
from flowforge.domain.prompt_builder import PromptPipeline
from flowforge.domain.artifact_manager import ArtifactManager
from flowforge.domain.memory import Memory, LessonLearnedStore

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
