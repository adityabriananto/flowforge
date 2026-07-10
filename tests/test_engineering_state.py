import pytest
import os
import yaml
from datetime import datetime
from flowforge.domain.engineering_state import (
    EngineeringState,
    ProjectState,
    WorkspaceState,
    MissionState,
    ProviderState,
    SessionState
)
from flowforge.services.workspace.state_loader import EngineeringStateLoader
from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
from flowforge.services.workspace.state_service import EngineeringStateService

@pytest.fixture
def refined_state_yaml():
    return """
version: "1"
project:
  id: "uuid-project-1234"
  name: "FlowForge Platform"
workspace:
  version: "1.0.0"
  engineering_phase: "coding"
mission:
  current_mission: "PROJECT-002"
  completed_missions: ["PROJECT-000", "PROJECT-001"]
  mission_history: ["PROJECT-000", "PROJECT-001", "PROJECT-002"]
provider:
  current_provider: "Claude"
  provider_history:
    - provider: "Gemini"
      mission: "PROJECT-000"
      started_at: "2026-07-10T08:00:00.000000"
      finished_at: "2026-07-10T08:30:00.000000"
session:
  current_session_id: "session-abc-123"
  latest_session_id: "session-xyz-987"
knowledge_state:
  knowledge:
    - id: "KNOW-001"
      title: "Repository Discovery"
      reference_path: "engineering/architecture/discovery.md"
      category: "repository"
      extracted_at: "2026-07-10T08:00:00.000000"
decision_state:
  decisions:
    - id: "DEC-001"
      title: "Use SQLite for metadata persistence"
      rationale: "Requires Zero-Config offline operation"
      mission: "PROJECT-000"
      artifact_reference: "docs/adr/ADR-001.md"
      decided_at: "2026-07-10T08:05:00.000000"
timeline_state:
  event_log:
    - id: "EV-001"
      event_type: "Mission Started"
      description: "Started mission: PROJECT-002"
      timestamp: "2026-07-10T09:01:00.000000"
open_questions:
  - id: "QST-001"
    title: "Support multiple concurrent active sessions?"
    description: "Assess concurrency and database locks in SqlAlchemy"
    mission: "PROJECT-002"
    status: "open"
    created_at: "2026-07-10T08:15:00.000000"
    resolved_at: null
blockers:
  - id: "BLK-001"
    description: "Redis server credentials are not configured"
    created_at: "2026-07-10T08:10:00.000000"
recommendations:
  - id: "REC-001"
    suggestion: "Initialize Distributed Worker test suite"
    proposed_at: "2026-07-10T08:15:00.000000"
"""

def test_loader_load_and_serialize_success(refined_state_yaml):
    state = EngineeringStateLoader.load_from_yaml(refined_state_yaml)
    assert state.project.id == "uuid-project-1234"
    assert state.project.name == "FlowForge Platform"
    assert state.mission.current_mission == "PROJECT-002"
    assert len(state.provider.provider_history) == 1
    assert state.provider.provider_history[0].provider == "Gemini"
    assert state.provider.provider_history[0].finished_at is not None
    assert state.knowledge_state.knowledge[0].category == "repository"
    assert state.decision_state.decisions[0].mission == "PROJECT-000"
    assert len(state.timeline_state.event_log) == 1
    assert state.timeline_state.event_log[0].event_type == "Mission Started"
    assert state.open_questions[0].status == "open"
    assert state.open_questions[0].resolved_at is None
    
    # Serialize back to dict
    serialized = EngineeringStateLoader.to_dict(state)
    assert serialized["project"]["id"] == "uuid-project-1234"
    assert serialized["version"] == "1"
    assert serialized["knowledge_state"]["knowledge"][0]["category"] == "repository"
    assert serialized["decision_state"]["decisions"][0]["mission"] == "PROJECT-000"
    assert serialized["timeline_state"]["event_log"][0]["event_type"] == "Mission Started"
    assert serialized["open_questions"][0]["status"] == "open"

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

def test_repository_save_and_load(tmp_path, refined_state_yaml):
    base_dir = str(tmp_path)
    
    # Setup folders
    os.makedirs(os.path.join(base_dir, "engineering"), exist_ok=True)
    
    repo = YAMLEngineeringStateRepository()
    state = EngineeringStateLoader.load_from_yaml(refined_state_yaml)
    
    # Save
    repo.save(state, base_path=base_dir)
    assert os.path.exists(os.path.join(base_dir, "engineering", "ENGINEERING_STATE.yaml"))
    
    # Load
    loaded_state = repo.load(base_path=base_dir)
    assert loaded_state.project.name == "FlowForge Platform"

def test_state_service_business_rules(tmp_path, refined_state_yaml):
    base_dir = str(tmp_path)
    os.makedirs(os.path.join(base_dir, "engineering"), exist_ok=True)
    
    repo = YAMLEngineeringStateRepository()
    state = EngineeringStateLoader.load_from_yaml(refined_state_yaml)
    repo.save(state, base_path=base_dir)
    
    service = EngineeringStateService(repo)
    
    # 1. Update active mission
    service.update_current_mission("PROJECT-003", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.mission.current_mission == "PROJECT-003"
    assert "PROJECT-002" in loaded.mission.mission_history
    assert loaded.timeline_state.event_log[-1].event_type == "Mission Started"
    
    # 2. Mark mission completed
    service.mark_mission_completed("PROJECT-003", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.mission.current_mission is None
    assert "PROJECT-003" in loaded.mission.completed_missions
    assert loaded.timeline_state.event_log[-1].event_type == "Mission Completed"
    
    # 3. Update provider
    service.update_provider("Ollama", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.provider.current_provider == "Ollama"
    assert len(loaded.provider.provider_history) == 2  # Gemini + Ollama
    assert loaded.timeline_state.event_log[-1].event_type == "Provider Changed"
    
    # 4. Add decisions, blockers, recommendations, knowledge, open questions
    service.add_decision("Use local git repo", "Zero cloud dependency needed", artifact_reference="docs/adr/ADR-002.md", base_path=base_dir)
    service.add_blocker("Ollama offline on local server", base_path=base_dir)
    service.add_recommendation("Restart ollama instance", base_path=base_dir)
    service.add_knowledge_reference("Repository structure analysis", "docs/discovery.md", category="repository", base_path=base_dir)
    service.add_open_question("Scale workers?", "Assess queue systems", base_path=base_dir)
    
    loaded = service.load_state(base_path=base_dir)
    assert len(loaded.decision_state.decisions) == 2  # DEC-001 + new one
    assert loaded.decision_state.decisions[-1].id == "DEC-002"
    assert loaded.decision_state.decisions[-1].rationale == "Zero cloud dependency needed"
    assert loaded.decision_state.decisions[-1].artifact_reference == "docs/adr/ADR-002.md"
    assert len(loaded.blockers) == 2  # BLK-001 + new one
    assert loaded.blockers[-1].id == "BLK-002"
    assert len(loaded.recommendations) == 2  # REC-001 + new one
    assert loaded.recommendations[-1].id == "REC-002"
    assert len(loaded.knowledge_state.knowledge) == 2  # KNOW-001 + new one
    assert loaded.knowledge_state.knowledge[-1].id == "KNOW-002"
    assert loaded.knowledge_state.knowledge[-1].category == "repository"
    assert len(loaded.open_questions) == 2  # QST-001 + new one
    assert loaded.open_questions[-1].id == "QST-002"
    assert loaded.open_questions[-1].status == "open"
    
    # Resolve question
    service.resolve_open_question("QST-002", base_path=base_dir)
    loaded = service.load_state(base_path=base_dir)
    assert loaded.open_questions[-1].status == "resolved"
    assert loaded.open_questions[-1].resolved_at is not None
    
    # 5. Build Resume Context
    restored = service.build_resume_context(base_path=base_dir)
    assert restored["project_name"] == "FlowForge Platform"
    assert restored["current_mission"] is None
    assert "Ollama offline on local server" in restored["active_blockers"]
    assert len(restored["latest_decisions"]) == 2  # Fits limit of latest 3
    assert restored["latest_decisions"][-1]["title"] == "Use local git repo"
    assert restored["latest_decisions"][-1]["artifact"] == "docs/adr/ADR-002.md"
    assert len(restored["open_questions"]) == 1  # Only open ones (QST-001 is open, QST-002 is resolved)
    assert restored["open_questions"][0]["title"] == "Support multiple concurrent active sessions?"
    assert len(restored["engineering_knowledge"]) == 2
    assert restored["engineering_knowledge"][-1]["category"] == "repository"
