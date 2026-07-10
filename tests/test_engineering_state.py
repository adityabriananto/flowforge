import pytest
import os
import yaml
from datetime import datetime
from flowforge.domain.engineering_state import (
    EngineeringState,
    ProjectState,
    WorkspaceState,
    MissionStateInfo,
    ProviderStateInfo,
    SessionStateInfo
)
from flowforge.services.workspace.state_loader import EngineeringStateLoader
from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
from flowforge.services.workspace.state_service import EngineeringStateService

@pytest.fixture
def sample_state_yaml():
    return """
version: "1"
project:
  id: "uuid-123"
  name: "FlowForge Test"
workspace:
  version: "1.0.0"
  engineering_phase: "init"
mission:
  current_mission: "PROJECT-000"
  completed_missions: []
  mission_history: []
provider:
  current_provider: "Claude"
  provider_history: []
session:
  current_session_id: "sess-001"
  latest_session_id: "sess-001"
knowledge: []
decisions: []
open_questions: []
blockers: []
recommendations: []
timeline: []
"""

def test_loader_load_and_serialize_success(sample_state_yaml):
    state = EngineeringStateLoader.load_from_yaml(sample_state_yaml)
    assert state.project.id == "uuid-123"
    assert state.project.name == "FlowForge Test"
    assert state.mission.current_mission == "PROJECT-000"
    
    # Serialize back to dict
    serialized = EngineeringStateLoader.to_dict(state)
    assert serialized["project"]["id"] == "uuid-123"
    assert serialized["version"] == "1"

def test_loader_unsupported_version():
    invalid_yaml = """
version: "2"
project:
  id: "1"
  name: "Invalid"
"""
    with pytest.raises(ValueError) as exc:
        EngineeringStateLoader.load_from_yaml(invalid_yaml)
    assert "Unsupported EngineeringState version" in str(exc.value)

def test_loader_invalid_yaml():
    with pytest.raises(ValueError) as exc:
        EngineeringStateLoader.load_from_yaml("invalid: : yaml")
    assert "Invalid YAML format" in str(exc.value)

def test_repository_save_and_load(tmp_path, sample_state_yaml):
    base_dir = str(tmp_path)
    
    # Setup folders
    os.makedirs(os.path.join(base_dir, "engineering"), exist_ok=True)
    
    repo = YAMLEngineeringStateRepository()
    state = EngineeringStateLoader.load_from_yaml(sample_state_yaml)
    
    # Save
    repo.save(state, base_path=base_dir)
    assert os.path.exists(os.path.join(base_dir, "engineering", "PROJECT_STATE.yaml"))
    
    # Load
    loaded_state = repo.load(base_path=base_dir)
    assert loaded_state.project.name == "FlowForge Test"

def test_state_service_business_rules(tmp_path, sample_state_yaml):
    base_dir = str(tmp_path)
    os.makedirs(os.path.join(base_dir, "engineering"), exist_ok=True)
    
    repo = YAMLEngineeringStateRepository()
    state = EngineeringStateLoader.load_from_yaml(sample_state_yaml)
    repo.save(state, base_path=base_dir)
    
    service = EngineeringStateService(repo)
    
    # 1. Update active mission
    service.update_current_mission("PROJECT-001", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.mission.current_mission == "PROJECT-001"
    assert "PROJECT-000" in loaded.mission.mission_history
    
    # 2. Mark mission completed
    service.mark_mission_completed("PROJECT-001", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.mission.current_mission is None
    assert "PROJECT-001" in loaded.mission.completed_missions
    
    # 3. Update provider
    service.update_provider("Gemini", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.provider.current_provider == "Gemini"
    assert "Claude" in loaded.provider.provider_history
    
    # 4. Add decisions, blockers, recommendations
    service.add_decision("Use local git repo", "Zero cloud dependency needed", base_path=base_dir)
    service.add_blocker("Ollama offline on local server", base_path=base_dir)
    service.add_recommendation("Restart ollama instance", base_path=base_dir)
    service.add_knowledge_reference("Repository structure analysis", "docs/discovery.md", base_path=base_dir)
    
    loaded = service.load_state(base_path=base_dir)
    assert len(loaded.decisions) == 1
    assert loaded.decisions[0].id == "DEC-001"
    assert loaded.decisions[0].rationale == "Zero cloud dependency needed"
    assert len(loaded.blockers) == 1
    assert loaded.blockers[0].id == "BLK-001"
    assert len(loaded.recommendations) == 1
    assert loaded.recommendations[0].id == "REC-001"
    assert len(loaded.knowledge) == 1
    assert loaded.knowledge[0].id == "KNOW-001"
    
    # 5. Context Restoration
    restored = service.resume_engineering_state(base_path=base_dir)
    assert restored["project_name"] == "FlowForge Test"
    assert restored["active_mission"] is None
    assert "Ollama offline on local server" in restored["active_blockers"]
    assert len(restored["recent_decisions"]) == 1
    assert restored["recent_decisions"][0] == ("Use local git repo", "Zero cloud dependency needed")
