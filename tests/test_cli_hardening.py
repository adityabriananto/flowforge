import pytest
import os
import uuid
import yaml
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
from flowforge.services.mission_loader import MissionLoader
from flowforge.entrypoints.cli.main import cmd_compile, cmd_mission

@pytest.fixture
def mock_hardened_workspace(tmp_path):
    base_dir = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    # Setup custom template
    template_dir = os.path.join(base_dir, "engineering", "missions", "templates")
    with open(os.path.join(template_dir, "mission.yaml"), "w", encoding="utf-8") as f:
        yaml.dump({
            "version": "1",
            "id": "template",
            "title": "Temp",
            "status": "BACKLOG",
            "priority": "low"
        }, f)
        
    return base_dir

def test_loader_graceful_non_uuid(mock_hardened_workspace):
    loader = MissionLoader()
    yaml_data = """
version: "1"
id: "PROJECT-001"
title: "Graceful non-UUID test"
status: "BACKLOG"
priority: "high"
"""
    mission = loader.load(yaml_data)
    assert mission.code == "PROJECT-001"
    # id is automatically parsed as a new valid UUID
    assert isinstance(mission.id, uuid.UUID)

def test_lifecycle_resolution_by_code(mock_hardened_workspace):
    # Create mission via code PROJECT-999
    MissionLifecycleManager.create_mission(
        title="Optimizer DB",
        description="Optimize indices",
        mission_id="PROJECT-999",
        base_path=mock_hardened_workspace
    )
    
    # 1. Start mission by Code
    active_path = MissionLifecycleManager.start_mission("PROJECT-999", base_path=mock_hardened_workspace)
    assert os.path.exists(active_path)
    
    # 2. Check PROJECT_STATE.yaml sync
    state = MissionLifecycleManager.get_project_state(mock_hardened_workspace)
    assert "PROJECT-999" in state["active_missions"]
    
    # 3. Complete mission by Code
    completed_path = MissionLifecycleManager.complete_mission("PROJECT-999", base_path=mock_hardened_workspace)
    assert os.path.exists(completed_path)

def test_cli_friendly_error_on_missing(mock_hardened_workspace, capsys):
    class Args:
        def __init__(self, mission_id):
            self.command = "mission"
            self.mission_command = "show"
            self.mission_id = mission_id

    # CLI show for unregistered code
    with pytest.raises(SystemExit):
        cmd_mission(Args("PROJECT-909"))
        
    captured = capsys.readouterr()
    assert "Mission PROJECT-909 not found" in captured.err
    assert "flowforge mission list" in captured.err

def test_cli_compile_by_mission_code(mock_hardened_workspace, monkeypatch):
    monkeypatch.chdir(mock_hardened_workspace)
    
    # Create the mission in backlog
    MissionLifecycleManager.create_mission(
        title="Test Compile By Code",
        description="Verify compiler integration",
        mission_id="PROJECT-101",
        base_path=mock_hardened_workspace
    )
    
    class CompileArgs:
        mission_file = "PROJECT-101"
        profile = None
        
    # Trigger compile
    cmd_compile(CompileArgs())
    # Expect compiled yaml exists in packages dir
    output_pkg = os.path.join(mock_hardened_workspace, ".flowforge", "packages", "PROJECT-101.package.yaml")
    assert os.path.exists(output_pkg)
