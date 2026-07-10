import pytest
import os
import yaml
from flowforge.services.workspace.detector import ProjectDetectorService
from flowforge.services.workspace.bootstrapper import SmartBootstrapper

def test_project_framework_detection(tmp_path):
    base_dir = str(tmp_path)
    
    # 1. Test Laravel detection
    with open(os.path.join(base_dir, "composer.json"), "w") as f:
        f.write("{}")
    with open(os.path.join(base_dir, "artisan"), "w") as f:
        f.write("")
    
    detector = ProjectDetectorService()
    details = detector.detect_project(base_dir)
    assert details["project_type"] == "Laravel"
    assert details["language"] == "PHP"
    
    # Clean up
    os.remove(os.path.join(base_dir, "composer.json"))
    os.remove(os.path.join(base_dir, "artisan"))

    # 2. Test Django detection
    with open(os.path.join(base_dir, "manage.py"), "w") as f:
        f.write("")
    details = detector.detect_project(base_dir)
    assert details["project_type"] == "Django"
    assert details["language"] == "Python"
    os.remove(os.path.join(base_dir, "manage.py"))

    # 3. Test React detection
    import json
    pkg_json_content = {
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "devDependencies": {
            "vite": "^4.0.0"
        }
    }
    with open(os.path.join(base_dir, "package.json"), "w") as f:
        json.dump(pkg_json_content, f)
    details = detector.detect_project(base_dir)
    assert details["project_type"] == "React"
    assert details["build_tool"] == "vite"
    os.remove(os.path.join(base_dir, "package.json"))

def test_git_safety_error(tmp_path):
    base_dir = str(tmp_path)
    # Running bootstrap on non-git dir should raise error
    with pytest.raises(RuntimeError) as exc:
        SmartBootstrapper.bootstrap(base_dir, force=False)
    assert "Not running inside a Git repository" in str(exc.value)

def test_smart_bootstrap_execution(tmp_path):
    base_dir = str(tmp_path)
    
    # Mock React project signatures
    import json
    pkg_json_content = {"dependencies": {"vue": "^3.0.0"}, "devDependencies": {"vite": "^4.0.0"}}
    with open(os.path.join(base_dir, "package.json"), "w") as f:
        json.dump(pkg_json_content, f)

    # Run bootstrapper bypass git check using force=True
    details = SmartBootstrapper.bootstrap(base_dir, force=True, prefix="VUE")
    
    assert details["project_type"] == "Vue"
    
    # Verify Folders exist
    assert os.path.exists(os.path.join(base_dir, "engineering", "missions", "backlog"))
    assert os.path.exists(os.path.join(base_dir, ".flowforge", "workspace"))
    
    # Verify WORKSPACE.yaml
    workspace_yaml_path = os.path.join(base_dir, "engineering", "WORKSPACE.yaml")
    assert os.path.exists(workspace_yaml_path)
    with open(workspace_yaml_path, "r") as f:
        ws_data = yaml.safe_load(f)
    assert ws_data["workspace_type"] == "Vue"
    assert ws_data["build_tool"] == "vite"

    # Verify initial mission
    init_mission_path = os.path.join(base_dir, "engineering", "missions", "backlog", "VUE-000.yaml")
    assert os.path.exists(init_mission_path)
    with open(init_mission_path, "r") as f:
        m_data = yaml.safe_load(f)
    assert m_data["id"] == "VUE-000"
    assert m_data["title"] == "Repository Discovery"

def test_bootstrap_idempotency(tmp_path):
    base_dir = str(tmp_path)
    
    # Run once
    SmartBootstrapper.bootstrap(base_dir, force=True, prefix="TEST")
    
    # Pre-write custom content to check idempotency
    workspace_yaml_path = os.path.join(base_dir, "engineering", "WORKSPACE.yaml")
    with open(workspace_yaml_path, "w") as f:
        f.write("custom_key: custom_val")
        
    # Run twice
    SmartBootstrapper.bootstrap(base_dir, force=True, prefix="TEST")
    
    # Verify it was NOT overwritten
    with open(workspace_yaml_path, "r") as f:
        content = f.read()
    assert "custom_key: custom_val" in content
