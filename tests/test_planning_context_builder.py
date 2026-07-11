import os
import json
import tomli
import yaml
import pytest
from flowforge.services.planning_context_builder import PlanningContextBuilder

def test_planning_context_builder_loads_metadata(tmp_path):
    base_path = str(tmp_path)
    eng_dir = os.path.join(base_path, "engineering")
    os.makedirs(eng_dir)
    
    workspace_path = os.path.join(eng_dir, "WORKSPACE.yaml")
    with open(workspace_path, "w", encoding="utf-8") as f:
        yaml.dump({
            "project_name": "BroDev Cashier",
            "framework": "Laravel",
            "language": "PHP",
            "project_type": "Unknown"
        }, f)
        
    project_state_path = os.path.join(eng_dir, "PROJECT_STATE.yaml")
    with open(project_state_path, "w", encoding="utf-8") as f:
        yaml.dump({
            "current_phase": "Business Workflow",
            "completed_missions": ["PROJECT-000", "PROJECT-001"],
            "active_missions": ["PROJECT-002"]
        }, f)
        
    builder = PlanningContextBuilder(base_path)
    context = builder.build_context()
    
    assert context.project_name == "BroDev Cashier"
    assert context.framework == "Laravel"
    assert context.language == "PHP"
    assert context.project_type == "Web Application"
    assert context.current_phase == "Business Workflow"
    assert context.completed_missions == ["PROJECT-000", "PROJECT-001"]
    assert context.existing_missions == 3

def test_planning_context_builder_missing_files(tmp_path):
    base_path = str(tmp_path)
    builder = PlanningContextBuilder(base_path)
    context = builder.build_context()
    
    expected_name = os.path.basename(os.path.abspath(base_path))
    assert context.project_name == expected_name
    assert context.framework == "Unknown"
    assert context.language == "Unknown"
    assert context.project_type == "Unknown"
    assert context.current_phase == "Project Initialization"
    assert context.completed_missions == []
    assert context.existing_missions == 0

def test_project_name_priority(tmp_path):
    base_path = str(tmp_path)
    # package.json should be overridden by directory name fallback
    # But wait, directory name comes BEFORE package.json in the new code.
    with open(os.path.join(base_path, "package.json"), "w") as f:
        json.dump({"name": "npm-project"}, f)
        
    builder = PlanningContextBuilder(base_path)
    context = builder.build_context()
    
    expected_name = os.path.basename(os.path.abspath(base_path))
    assert context.project_name == expected_name

def test_project_type_resolution(tmp_path):
    base_path = str(tmp_path)
    eng_dir = os.path.join(base_path, "engineering")
    os.makedirs(eng_dir)
    
    workspace_path = os.path.join(eng_dir, "WORKSPACE.yaml")
    with open(workspace_path, "w", encoding="utf-8") as f:
        yaml.dump({"framework": "Spring Boot"}, f)
        
    builder = PlanningContextBuilder(base_path)
    context = builder.build_context()
    assert context.project_type == "Backend Service"

def test_current_phase_resolution_from_latest_mission(tmp_path):
    base_path = str(tmp_path)
    eng_dir = os.path.join(base_path, "engineering")
    os.makedirs(eng_dir)
    missions_dir = os.path.join(eng_dir, "missions", "completed")
    os.makedirs(missions_dir)
    
    project_state_path = os.path.join(eng_dir, "PROJECT_STATE.yaml")
    with open(project_state_path, "w", encoding="utf-8") as f:
        yaml.dump({
            "completed_missions": ["PROJECT-000", "PROJECT-003"]
        }, f)
        
    # Create latest mission
    mission_path = os.path.join(missions_dir, "PROJECT-003.yaml")
    with open(mission_path, "w", encoding="utf-8") as f:
        yaml.dump({"title": "Business Workflow Setup"}, f)
        
    builder = PlanningContextBuilder(base_path)
    context = builder.build_context()
    assert context.current_phase == "Architecture Design"
