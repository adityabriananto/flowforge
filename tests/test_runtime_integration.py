import pytest
import os
import yaml
from flowforge.ports.ai_provider import AIProvider
from flowforge.domain.mission_package import MissionPackage
from flowforge.domain.engineering_session import SessionStatus
from flowforge.services.compiler.compiler import MissionPackageCompiler
from flowforge.services.workspace.session_service import EngineeringSessionService
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.services.runtime.engine import AIRuntimeEngine
from flowforge.adapters.workspace.yaml_session_repository import YAMLEngineeringSessionRepository

class FakeAIProvider(AIProvider):
    def name(self) -> str:
        return "FakeProvider"

    def health(self) -> dict:
        return {"healthy": True, "available": True}

    def execute(self, mission_package: MissionPackage, **kwargs) -> dict:
        return {
            "status": "SUCCESS",
            "summary": "Completed code implementation for PROJECT-001.",
            "artifacts": ["src/repository.py"],
            "decisions": [
                {
                    "title": "Decoupled AI Engine",
                    "rationale": "Avoid provider lock-in",
                    "artifact_reference": "docs/adr/ADR-013.md"
                }
            ],
            "files_changed": ["src/repository.py"],
            "warnings": ["Deprecation warning in SQLite driver"],
            "blockers": ["Network latency"],
            "recommendations": ["Optimize backend queries"],
            "handover_summary": "DB integration is complete. Handing over to QA worker."
        }

@pytest.fixture
def workspace_setup(tmp_path):
    base_dir = str(tmp_path)
    
    # 1. Setup engineering dirs
    os.makedirs(os.path.join(base_dir, "engineering", "missions", "active"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "engineering", "missions", "completed"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "engineering", "missions", "backlog"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "engineering", "missions", "templates"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, ".flowforge", "logs"), exist_ok=True)
    
    # 2. Write a raw active mission file
    mission_data = {
        "id": "11111111-2222-3333-4444-555555555555",
        "code": "PROJECT-001",
        "title": "Database Schema Setup",
        "description": "Initialize database connection pool and models",
        "status": "ACTIVE",
        "priority": "high",
        "version": "1",
        "created_at": "2026-07-10T08:00:00Z"
    }
    
    mission_path = os.path.join(base_dir, "engineering", "missions", "active", "mission_11111111.yaml")
    with open(mission_path, "w", encoding="utf-8") as f:
        yaml.dump(mission_data, f)
        
    return base_dir

def test_e2e_runtime_orchestration_pipeline(workspace_setup):
    base_dir = workspace_setup
    
    # 1. Setup Services & Ports
    compiler = MissionPackageCompiler()
    
    session_repo = YAMLEngineeringSessionRepository()
    session_service = EngineeringSessionService(session_repo)
    
    provider_registry = AIRuntimeProviderRegistry()
    fake_provider = FakeAIProvider()
    provider_registry.register("FakeProvider", fake_provider, is_default=True)
    
    # 2. Initialize Engine
    engine = AIRuntimeEngine(
        compiler=compiler,
        session_service=session_service,
        provider_registry=provider_registry
    )
    
    # 3. Execute mission PROJECT-001
    result = engine.execute_mission("PROJECT-001", base_path=base_dir)
    
    # 4. Verify outcomes
    assert result["status"] == "SUCCESS"
    assert result["session_id"] is not None
    assert "Completed code implementation for PROJECT-001" in result["summary_report"]
    
    # Verify Sesi log file exists on disk
    session_file_path = os.path.join(base_dir, ".flowforge", "logs", f"session_{result['session_id']}.yaml")
    assert os.path.exists(session_file_path)
    
    # Verify session status is COMPLETED
    loaded_session = session_service.load_session(result["session_id"], base_path=base_dir)
    assert loaded_session.metadata.status == SessionStatus.COMPLETED
    assert "src/repository.py" in loaded_session.artifacts
    assert "Network latency" in loaded_session.blockers
    

