import pytest
import os
import uuid
import yaml
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager
from flowforge.entrypoints.cli.main import cmd_mission

@pytest.fixture
def mock_workspace(tmp_path):
    base_dir = str(tmp_path)
    # Initialize workspace structure & copy template manually
    EngineeringWorkspace.initialize_workspace(base_dir)
    
    # Write a dummy template mission
    template_dir = os.path.join(base_dir, "engineering", "missions", "templates")
    with open(os.path.join(template_dir, "mission.yaml"), "w", encoding="utf-8") as f:
        yaml.dump({
            "version": "1",
            "id": "template",
            "title": "Temp",
            "status": "BACKLOG",
            "priority": "low",
            "deliverables": [],
            "definition_of_done": []
        }, f)
        
    return base_dir

def test_create_mission_lifecycle(mock_workspace):
    m_id = str(uuid.uuid4())
    title = "Test CLI mission"
    desc = "CLI mission description"
    
    # Create
    file_path = MissionLifecycleManager.create_mission(title, desc, m_id, base_path=mock_workspace)
    assert os.path.exists(file_path)
    assert os.path.join("engineering", "missions", "backlog") in file_path
    
    # Load and verify
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["id"] == m_id
    assert data["title"] == title
    assert data["status"] == "BACKLOG"
    
    # Verify duplicate error
    with pytest.raises(ValueError) as exc:
        MissionLifecycleManager.create_mission(title, desc, m_id, base_path=mock_workspace)
    assert "Duplicate Mission ID" in str(exc.value)

def test_list_and_show_missions(mock_workspace):
    m_id = str(uuid.uuid4())
    MissionLifecycleManager.create_mission("Title 1", "Desc 1", m_id, base_path=mock_workspace)
    
    # List
    grouped = MissionLifecycleManager.list_missions(base_path=mock_workspace)
    assert len(grouped["backlog"]) == 1
    assert grouped["backlog"][0]["id"] == m_id
    assert grouped["backlog"][0]["title"] == "Title 1"
    
    # Show
    loaded = MissionLifecycleManager.show_mission(m_id, base_path=mock_workspace)
    assert loaded.id == uuid.UUID(m_id)
    assert loaded.title == "Title 1"

def test_mission_state_transitions(mock_workspace):
    m_id = str(uuid.uuid4())
    MissionLifecycleManager.create_mission("Transition M", "Desc", m_id, base_path=mock_workspace)
    
    # Verify starting backlog -> active
    active_path = MissionLifecycleManager.start_mission(m_id, base_path=mock_workspace)
    assert os.path.exists(active_path)
    assert os.path.join("engineering", "missions", "active") in active_path
    
    # Verify PROJECT_STATE.yaml
    state = MissionLifecycleManager.get_project_state(mock_workspace)
    assert m_id in state["active_missions"]
    
    # Verify file inside
    with open(active_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["status"] == "ACTIVE"

    # Verify transition validation (cannot start again)
    with pytest.raises(ValueError) as exc:
        MissionLifecycleManager.start_mission(m_id, base_path=mock_workspace)
    assert "cannot start" in str(exc.value)

    # Complete mission: active -> completed
    completed_path = MissionLifecycleManager.complete_mission(m_id, base_path=mock_workspace)
    assert os.path.exists(completed_path)
    assert os.path.join("engineering", "missions", "completed") in completed_path
    
    # Verify PROJECT_STATE.yaml update
    state = MissionLifecycleManager.get_project_state(mock_workspace)
    assert m_id not in state["active_missions"]
    assert m_id in state["completed_missions"]
    
    # Verify file inside
    with open(completed_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["status"] == "DONE"

def test_cli_command_routing(mock_workspace, monkeypatch):
    # Route path to temp workspace mock
    monkeypatch.chdir(mock_workspace)
    
    class Args:
        def __init__(self, cmd, **kwargs):
            self.command = "mission"
            self.mission_command = cmd
            for k, v in kwargs.items():
                setattr(self, k, v)

    # CLI mission new
    m_id = str(uuid.uuid4())
    args_new = Args("new", title="CLI Test", desc="CLI Desc", id=m_id)
    cmd_mission(args_new)
    
    backlog_path = os.path.join(mock_workspace, "engineering", "missions", "backlog", f"{m_id}.yaml")
    assert os.path.exists(backlog_path)
    
    # CLI mission start
    args_start = Args("start", mission_id=m_id)
    cmd_mission(args_start)
    assert os.path.exists(os.path.join(mock_workspace, "engineering", "missions", "active", f"{m_id}.yaml"))
