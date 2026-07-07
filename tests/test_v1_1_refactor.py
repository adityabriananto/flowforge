import sys
import os
import uuid
import pytest
from unittest.mock import MagicMock

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig
from flowforge.domain.engine import StateMachine, InvalidTransitionError
from flowforge.domain.yaml_loader import load_workflow_from_yaml
from flowforge.domain.capability_resolver import CapabilityResolver
from flowforge.domain.prompt_builder import PromptBuilder, ContextLoader
from flowforge.domain.artifact_manager import ArtifactManager
from flowforge.domain.memory import Memory

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

# 2. Test YAML Loader
def test_yaml_loader():
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
    workflow = load_workflow_from_yaml(yaml_content)
    assert workflow.name == "AI Coder Workflow"
    assert workflow.initial_state == "ANALYSIS"
    assert "ANALYSIS" in workflow.states
    assert "ARCHITECTURE" in workflow.states
    assert workflow.states["ARCHITECTURE"].require_human is True
    
    # Check transitions mapping
    assert workflow.transitions[("ANALYSIS", "SUCCESS")] == "ARCHITECTURE"

# 3. Test Capability Resolver
def test_capability_resolver():
    resolver = CapabilityResolver()
    
    mock_claude = MagicMock()
    mock_codex = MagicMock()
    
    resolver.register_provider("claude", mock_claude)
    resolver.register_provider("codex", mock_codex)
    
    # Resolve architecture capability -> Claude
    provider = resolver.resolve_best_provider("architecture")
    assert provider == mock_claude
    
    # Resolve coding capability -> Codex
    provider = resolver.resolve_best_provider("coding")
    assert provider == mock_codex

# 4. Test Prompt Builder
def test_prompt_builder(tmp_path):
    builder = PromptBuilder()
    
    # Create target file for context loading
    code_file = tmp_path / "utils.py"
    code_file.write_text("def test(): pass")
    
    # Load file context
    content = ContextLoader.load_file_content(str(code_file))
    assert content == "def test(): pass"
    
    # Test build prompt
    builder.add_template("test_tpl", "Review this code:\n{code}\nFocus: {focus}")
    prompt = builder.build_prompt("test_tpl", {"code": content, "focus": "security"})
    
    assert "Review this code:\ndef test(): pass" in prompt
    assert "Focus: security" in prompt

# 5. Test Artifact Manager
def test_artifact_manager(tmp_path):
    manager = ArtifactManager(storage_dir=str(tmp_path))
    instance_id = uuid.uuid4()
    
    # Create artifact
    artifact = manager.create_artifact(
        instance_id=instance_id,
        name="architecture.md",
        path="docs/architecture.md",
        content="# System Architecture"
    )
    
    assert artifact.name == "architecture.md"
    assert artifact.status == "PENDING_REVIEW"
    assert artifact.version == 1
    
    # Verify file is written
    full_path = tmp_path / "docs" / "architecture.md"
    assert os.path.exists(full_path)
    assert full_path.read_text() == "# System Architecture"

    # Update status
    updated = manager.update_status(artifact.id, "APPROVED", feedback="Looks solid!")
    assert updated.status == "APPROVED"
    assert updated.feedback == "Looks solid!"

# 6. Test Memory Module
@pytest.mark.asyncio
async def test_memory_module(tmp_path):
    memory = Memory(memory_dir=str(tmp_path))
    
    memory.add_entry("system", "Initialize AI Worker context")
    memory.add_entry("assistant", "Design layout")
    
    assert len(memory.get_history()) == 2
    assert memory.get_history()[0].role == "system"
    
    # Save and Load from disk
    await memory.save_to_disk("test_mem.json")
    
    # Check file exists on disk
    file_path = tmp_path / "test_mem.json"
    assert os.path.exists(file_path)
    
    # Load back in new memory instance
    new_memory = Memory(memory_dir=str(tmp_path))
    await new_memory.load_from_disk("test_mem.json")
    
    assert len(new_memory.get_history()) == 2
    assert new_memory.get_history()[0].content == "Initialize AI Worker context"

# 7. Test Plugin Auto-Discovery
def test_plugin_auto_discovery():
    from flowforge.domain.plugin_manager import PluginManager
    manager = PluginManager()
    # Call discover_and_register_plugins and check it runs without error
    manager.discover_and_register_plugins()
    assert len(manager.plugins) == 0  # No plugins registered in test env

