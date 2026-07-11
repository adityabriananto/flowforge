import os
import yaml
import pytest
from flowforge.services.workspace.bootstrapper import SmartBootstrapper
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

@pytest.fixture
def temp_workspace(tmp_path):
    base_dir = str(tmp_path)
    # Mock git repository directory to pass git safety check
    os.makedirs(os.path.join(base_dir, ".git"), exist_ok=True)
    return base_dir

def test_smart_bootstrap_populates_project_state_metadata(temp_workspace):
    # Execute bootstrap
    details = SmartBootstrapper.bootstrap(base_path=temp_workspace, force=False, prefix="TESTPROJ")
    
    # Verify PROJECT_STATE.yaml populate
    state_path = os.path.join(temp_workspace, "engineering", "PROJECT_STATE.yaml")
    assert os.path.exists(state_path)
    
    with open(state_path, "r", encoding="utf-8") as f:
        state_data = yaml.safe_load(f)
        
    assert state_data["version"] == "1"
    project_meta = state_data["project"]
    assert project_meta["id"] is not None
    assert project_meta["framework"] == details["framework"]
    assert project_meta["language"] == details["language"]
    assert project_meta["project_type"] == details["project_type"]
    assert project_meta["workspace_version"] == "1.0.0"
    assert project_meta["current_phase"] == "discovery"

def test_smart_bootstrap_creates_intelligent_initial_mission(temp_workspace):
    details = SmartBootstrapper.bootstrap(base_path=temp_workspace, force=False, prefix="TESTPROJ")
    
    # Verify initial mission creation TESTPROJ-000
    mission_file = os.path.join(temp_workspace, "engineering", "missions", "backlog", "TESTPROJ-000.yaml")
    assert os.path.exists(mission_file)
    
    with open(mission_file, "r", encoding="utf-8") as f:
        mission_data = yaml.safe_load(f)
        
    assert mission_data["code"] == "TESTPROJ-000"
    assert mission_data["title"] == "Repository Discovery"
    assert "Repository Structure Report" in mission_data["deliverables"]
    assert "Repository analyzed" in mission_data["definition_of_done"]
    assert len(mission_data["constraints"]) >= 2
    
    # Technology Stack deliverable should be rendered with project details
    tech_stack_rendered = f"Technology Stack Report ({details['framework']} on {details['language']})"
    assert tech_stack_rendered in mission_data["deliverables"]
