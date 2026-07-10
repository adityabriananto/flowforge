import pytest
import os
import shutil
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace

def test_initialize_workspace(tmp_path):
    base_dir = str(tmp_path)
    
    # Run initialization
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    # Check Engineering Directories
    for folder in EngineeringWorkspace.ENGINEERING_DIRS:
        assert os.path.exists(os.path.join(base_dir, folder))
        
    # Check Runtime Directories
    for folder in EngineeringWorkspace.FLOWFORGE_DIRS:
        assert os.path.exists(os.path.join(base_dir, folder))

def test_move_mission_file_success(tmp_path):
    base_dir = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    # Write a mock mission file in backlog
    backlog_dir = os.path.join(base_dir, "engineering", "missions", "backlog")
    mission_file = "test_mission.yaml"
    with open(os.path.join(backlog_dir, mission_file), "w") as f:
        f.write("title: Test Mission")
        
    # Move: backlog -> active
    dest = EngineeringWorkspace.move_mission_file(mission_file, "backlog", "active", base_path=base_dir)
    assert os.path.exists(dest)
    assert not os.path.exists(os.path.join(backlog_dir, mission_file))
    assert os.path.basename(dest) == mission_file
    
    # Move: active -> completed
    dest_completed = EngineeringWorkspace.move_mission_file(mission_file, "active", "completed", base_path=base_dir)
    assert os.path.exists(dest_completed)
    assert not os.path.exists(dest)

def test_move_mission_file_source_missing(tmp_path):
    base_dir = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    # Attempt moving a non-existent file
    with pytest.raises(FileNotFoundError) as exc:
        EngineeringWorkspace.move_mission_file("ghost.yaml", "backlog", "active", base_path=base_dir)
    assert "not found in 'backlog' folder" in str(exc.value)

def test_move_mission_file_invalid_state(tmp_path):
    base_dir = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    with pytest.raises(ValueError) as exc:
        EngineeringWorkspace.move_mission_file("m.yaml", "backlog", "deleted", base_path=base_dir)
    assert "Invalid state transition" in str(exc.value)

def test_standard_templates_exist():
    # Verify templates are created in the actual project directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_dir = os.path.join(root_dir, "engineering", "missions", "templates")
    
    assert os.path.exists(templates_dir)
    assert os.path.exists(os.path.join(templates_dir, "mission.yaml"))
    assert os.path.exists(os.path.join(templates_dir, "rfc.md"))
    assert os.path.exists(os.path.join(templates_dir, "adr.md"))
    assert os.path.exists(os.path.join(templates_dir, "sprint.md"))
    assert os.path.exists(os.path.join(templates_dir, "review.md"))
