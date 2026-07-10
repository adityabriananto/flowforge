import pytest
import os
import yaml
from datetime import datetime
from flowforge.domain.engineering_session import EngineeringSession, SessionMetadata, SessionStatus
from flowforge.services.workspace.session_loader import EngineeringSessionLoader
from flowforge.adapters.workspace.yaml_session_repository import YAMLEngineeringSessionRepository
from flowforge.services.workspace.session_service import EngineeringSessionService
from flowforge.domain.engineering_state import EngineeringState
from flowforge.services.workspace.state_loader import EngineeringStateLoader
from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
from flowforge.services.workspace.state_service import EngineeringStateService

@pytest.fixture
def sample_session_yaml():
    return """
version: "1"
metadata:
  session_id: "session-uuid-12345"
  provider: "Claude"
  mission: "PROJECT-002"
  started_at: "2026-07-10T08:00:00.000000"
  finished_at: "2026-07-10T08:05:00.000000"
  duration_seconds: 300.0
  status: "ACTIVE"
summary: "Metadata DB indexing implementation."
artifacts:
  - "docs/discovery.md"
decisions:
  - title: "Use SQLite for metadata persistence"
    rationale: "Requires Zero-Config offline operation"
    artifact_reference: "docs/adr/ADR-001.md"
    decided_at: "2026-07-10T08:05:00.000000"
files_changed: []
warnings: []
open_questions: []
blockers: []
recommendations: []
handover_summary: null
"""

@pytest.fixture
def sample_state_yaml():
    return """
version: "1"
project:
  id: "uuid-123"
  name: "FlowForge Platform"
workspace:
  version: "1.0.0"
  engineering_phase: "coding"
mission:
  current_mission: "PROJECT-002"
  completed_missions: []
  mission_history: []
provider:
  current_provider: null
  provider_history: []
session:
  current_session_id: null
  latest_session_id: null
knowledge_state:
  knowledge: []
decision_state:
  decisions: []
timeline_state:
  event_log: []
open_questions: []
blockers: []
recommendations: []
"""

def test_session_loader_success(sample_session_yaml):
    session = EngineeringSessionLoader.load_from_yaml(sample_session_yaml)
    assert session.metadata.session_id == "session-uuid-12345"
    assert session.metadata.provider == "Claude"
    assert session.metadata.status == SessionStatus.ACTIVE
    assert len(session.artifacts) == 1
    
    serialized = EngineeringSessionLoader.to_dict(session)
    assert serialized["metadata"]["session_id"] == "session-uuid-12345"
    assert serialized["version"] == "1"

def test_session_repository_persistence(tmp_path, sample_session_yaml):
    base_dir = str(tmp_path)
    os.makedirs(os.path.join(base_dir, ".flowforge", "logs"), exist_ok=True)
    
    repo = YAMLEngineeringSessionRepository()
    session = EngineeringSessionLoader.load_from_yaml(sample_session_yaml)
    
    repo.save(session, base_path=base_dir)
    assert os.path.exists(os.path.join(base_dir, ".flowforge", "logs", "session_session-uuid-12345.yaml"))
    
    loaded = repo.load("session-uuid-12345", base_path=base_dir)
    assert loaded.metadata.provider == "Claude"

def test_session_service_lifecycle_and_immutability(tmp_path):
    base_dir = str(tmp_path)
    os.makedirs(os.path.join(base_dir, ".flowforge", "logs"), exist_ok=True)
    
    repo = YAMLEngineeringSessionRepository()
    service = EngineeringSessionService(repo)
    
    # 1. Create Sesi
    session = service.create_session("Gemini", "PROJECT-999", session_id="sess-999", base_path=base_dir)
    assert session.metadata.status == SessionStatus.CREATED
    
    # 2. Start Sesi
    service.start_session("sess-999", base_path=base_dir)
    loaded = service.load_session("sess-999", base_path=base_dir)
    assert loaded.metadata.status == SessionStatus.ACTIVE
    
    # 3. Add details
    service.add_artifact("sess-999", "docs/roadmap.md", base_path=base_dir)
    service.add_decision("sess-999", "Ollama local", "Cost reduction", base_path=base_dir)
    service.add_warning("sess-999", "Local connection is slow", base_path=base_dir)
    service.add_blocker("sess-999", "Local GPU memory limit", base_path=base_dir)
    service.add_recommendation("sess-999", "Use cloud fallback", base_path=base_dir)
    
    loaded = service.load_session("sess-999", base_path=base_dir)
    assert len(loaded.artifacts) == 1
    assert len(loaded.decisions) == 1
    assert len(loaded.warnings) == 1
    assert len(loaded.blockers) == 1
    assert len(loaded.recommendations) == 1
    
    # 4. Complete Sesi (Transisi Final)
    service.complete_session("sess-999", "Discovery completed", "Handover to Claude", base_path=base_dir)
    finalized = service.load_session("sess-999", base_path=base_dir)
    assert finalized.metadata.status == SessionStatus.COMPLETED
    assert finalized.metadata.finished_at is not None
    assert finalized.metadata.duration_seconds is not None
    
    # 5. Immutability Assertion (Mencoba mutasi data pada sesi final harus raises RuntimeError)
    with pytest.raises(RuntimeError) as exc:
        service.add_blocker("sess-999", "New Blocker", base_path=base_dir)
    assert "Immutable Session" in str(exc.value)

def test_session_state_integration(tmp_path, sample_session_yaml, sample_state_yaml):
    base_dir = str(tmp_path)
    os.makedirs(os.path.join(base_dir, ".flowforge", "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "engineering"), exist_ok=True)
    
    # Setup Repository & Services
    session_repo = YAMLEngineeringSessionRepository()
    session_service = EngineeringSessionService(session_repo)
    
    state_repo = YAMLEngineeringStateRepository()
    state_service = EngineeringStateService(state_repo)
    
    # Save Initial State & Session
    state = EngineeringStateLoader.load_from_yaml(sample_state_yaml)
    state_repo.save(state, base_path=base_dir)
    
    session = EngineeringSessionLoader.load_from_yaml(sample_session_yaml)
    session_repo.save(session, base_path=base_dir)
    
    # Add items to session before completing
    session_service.add_blocker("session-uuid-12345", "GPU limit", base_path=base_dir)
    session_service.add_recommendation("session-uuid-12345", "Upgrade hardware", base_path=base_dir)
    
    # Complete and sync state
    session_service.complete_session(
        session_id="session-uuid-12345",
        summary="DB indices optimization done.",
        handover_summary="Resume at PROJECT-003.",
        base_path=base_dir,
        state_service=state_service
    )
    
    # Load state and verify integrated data
    loaded_state = state_service.load_state(base_path=base_dir)
    assert loaded_state.mission.current_mission is None
    assert "PROJECT-002" in loaded_state.mission.completed_missions
    assert loaded_state.provider.current_provider == "Claude"
    assert len(loaded_state.knowledge_state.knowledge) == 1
    assert loaded_state.knowledge_state.knowledge[0].reference_path == "docs/discovery.md"
    assert len(loaded_state.decision_state.decisions) == 1
    assert loaded_state.decision_state.decisions[0].title == "Use SQLite for metadata persistence"
    assert len(loaded_state.blockers) == 1
    assert loaded_state.blockers[0].description == "GPU limit"
    assert len(loaded_state.recommendations) == 1
    assert loaded_state.recommendations[0].suggestion == "Upgrade hardware"
    
    # Handover Generation
    handover = session_service.generate_handover("session-uuid-12345", base_path=base_dir)
    assert handover["session_id"] == "session-uuid-12345"
    assert "GPU limit" in handover["active_blockers"]
    assert handover["handover_summary"] == "Resume at PROJECT-003."
    
    # Export Summary
    summary_str = session_service.export_session_summary("session-uuid-12345", base_path=base_dir)
    assert "Status: COMPLETED" in summary_str
    assert "Use SQLite for metadata persistence" in summary_str
