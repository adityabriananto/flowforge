import os
import pytest
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace

def test_cli_mission_start_none_type_regression(tmp_path):
    """
    FF-030 Regression Test:
    Ensures that starting a mission when active_missions or completed_missions is None
    does not throw a NoneType exception.
    """
    # Initialize workspace
    EngineeringWorkspace.initialize_workspace(str(tmp_path))
    
    # Create a PROJECT_STATE.yaml with None for lists
    state_file = tmp_path / "engineering" / "PROJECT_STATE.yaml"
    state_file.write_text("version: '1'\nactive_missions:\ncompleted_missions:\n")
    
    # Create a mission in backlog
    backlog_dir = tmp_path / "engineering" / "missions" / "backlog"
    mission_file = backlog_dir / "PROJECT-REG.yaml"
    mission_file.write_text("id: PROJECT-REG\nstatus: BACKLOG\n")
    
    # Run start mission
    try:
        new_path = MissionLifecycleManager.start_mission("PROJECT-REG", str(tmp_path))
    except TypeError as e:
        pytest.fail(f"Regression detected: {e}")
    
    # Verify move
    assert os.path.exists(new_path)
    
    # Verify state file parsing didn't fail and added the mission
    state_content = state_file.read_text()
    assert "- PROJECT-REG" in state_content
