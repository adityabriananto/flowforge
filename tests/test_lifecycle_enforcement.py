import os
import yaml
import pytest
from flowforge.services.runtime.engine import AIRuntimeEngine
from flowforge.services.workspace.bootstrapper import SmartBootstrapper
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.services.runtime.provider_config_loader import GenericCLIProviderAdapter

@pytest.fixture
def mock_lifecycle_workspace(tmp_path):
    base_dir = str(tmp_path)
    
    # Mock Git repo
    os.makedirs(os.path.join(base_dir, ".git"), exist_ok=True)
    
    # Bootstrap workspace
    SmartBootstrapper.bootstrap(base_path=base_dir, force=False, prefix="TESTPROJ")
    
    return base_dir

def test_engine_guard_refuses_backlog_mission(mock_lifecycle_workspace):
    base_dir = mock_lifecycle_workspace
    
    # 1. Setup Services & Ports
    from flowforge.services.compiler.compiler import MissionPackageCompiler
    from flowforge.services.workspace.state_service import EngineeringStateService
    from flowforge.services.workspace.session_service import EngineeringSessionService
    from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
    from flowforge.adapters.workspace.yaml_session_repository import YAMLEngineeringSessionRepository

    compiler = MissionPackageCompiler()
    state_service = EngineeringStateService(YAMLEngineeringStateRepository())
    session_service = EngineeringSessionService(YAMLEngineeringSessionRepository())
    
    registry = AIRuntimeProviderRegistry()
    dummy_provider = GenericCLIProviderAdapter("mock-provider", "echo 1")
    registry.register("mock-provider", dummy_provider, is_default=True)
    
    engine = AIRuntimeEngine(
        compiler=compiler,
        state_service=state_service,
        session_service=session_service,
        provider_registry=registry
    )
    
    # 2. Assert TESTPROJ-000 is initially in BACKLOG and running it raises RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        engine.execute_mission(mission_code="TESTPROJ-000", base_path=base_dir)
        
    assert "currently in BACKLOG" in str(excinfo.value)
    assert "Run 'flowforge mission start TESTPROJ-000' before executing" in str(excinfo.value)

def test_engine_allows_active_mission(mock_lifecycle_workspace):
    base_dir = mock_lifecycle_workspace
    
    # 1. Setup Services & Ports
    from flowforge.services.compiler.compiler import MissionPackageCompiler
    from flowforge.services.workspace.state_service import EngineeringStateService
    from flowforge.services.workspace.session_service import EngineeringSessionService
    from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
    from flowforge.adapters.workspace.yaml_session_repository import YAMLEngineeringSessionRepository

    compiler = MissionPackageCompiler()
    state_service = EngineeringStateService(YAMLEngineeringStateRepository())
    session_service = EngineeringSessionService(YAMLEngineeringSessionRepository())
    
    registry = AIRuntimeProviderRegistry()
    dummy_provider = GenericCLIProviderAdapter("mock-provider", "echo 1")
    registry.register("mock-provider", dummy_provider, is_default=True)
    
    engine = AIRuntimeEngine(
        compiler=compiler,
        state_service=state_service,
        session_service=session_service,
        provider_registry=registry
    )
    
    # 2. Move mission to ACTIVE state using standard workspace logic
    # Locate mission file in backlog
    backlog_path = os.path.join(base_dir, "engineering", "missions", "backlog", "TESTPROJ-000.yaml")
    assert os.path.exists(backlog_path)
    
    # Modify mission status directly to ACTIVE and move it to active directory
    with open(backlog_path, "r", encoding="utf-8") as f:
        m_data = yaml.safe_load(f)
    
    m_data["status"] = "ACTIVE"
    
    active_dir = os.path.join(base_dir, "engineering", "missions", "active")
    os.makedirs(active_dir, exist_ok=True)
    active_path = os.path.join(active_dir, "TESTPROJ-000.yaml")
    
    with open(active_path, "w", encoding="utf-8") as f:
        yaml.dump(m_data, f)
        
    os.remove(backlog_path)
    
    # 3. Running ACTIVE mission should now bypass the guard and execute successfully
    summary = engine.execute_mission(mission_code="TESTPROJ-000", base_path=base_dir)
    assert summary["status"] == "SUCCESS"
