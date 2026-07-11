import os
import yaml
import pytest
from flowforge.domain.mission import Mission
from flowforge.services.compiler.compiler import MissionPackageCompiler

@pytest.fixture
def enriched_workspace(tmp_path):
    base_dir = str(tmp_path)
    
    # 1. Setup engineering dirs
    os.makedirs(os.path.join(base_dir, "engineering", "decisions"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "engineering", "architecture"), exist_ok=True)
    
    # 2. Write WORKSPACE.yaml
    workspace_data = {
        "workspace_type": "backend",
        "language": "python",
        "framework": "fastapi",
        "package_manager": "pip",
        "build_tool": "poetry"
    }
    with open(os.path.join(base_dir, "engineering", "WORKSPACE.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(workspace_data, f)
        
    # 3. Write PROJECT_STATE.yaml
    state_data = {
        "version": "1",
        "project": {
            "id": "proj-abc",
            "name": "MeetingIntelligence",
            "framework": "fastapi",
            "language": "python",
            "project_type": "backend",
            "workspace_version": "1.0.0",
            "current_phase": "development",
            "created_at": "2026-07-11T00:00:00Z"
        },
        "active_missions": [],
        "completed_missions": []
    }
    with open(os.path.join(base_dir, "engineering", "PROJECT_STATE.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(state_data, f)
        
    # 4. Write standard files to base_dir
    with open(os.path.join(base_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Meeting Intelligence")
        
    with open(os.path.join(base_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
        f.write("[project]\nversion = '1.3.0'")
        
    return base_dir

def test_compiler_enrichment_pipeline(enriched_workspace):
    base_dir = enriched_workspace
    
    # Instantiate Mission
    mission = Mission(
        id="123",
        code="PROJECT-001",
        title="Database Setup",
        description="Configure MySQL database pooling",
        status="READY",
        priority="high",
        version="1",
        goal="Establish baseline pooling",
        deliverables=["Database Report", "Code Implementation"],
        definition_of_done=["Linter checks pass"],
        constraints=["Max size 10"],
        references=[]
    )
    
    compiler = MissionPackageCompiler(
        rules_file_path=os.path.join(base_dir, "engineering", "decisions", "AGENTS.md"),
        references_dir=os.path.join(base_dir, "engineering", "architecture")
    )
    
    # Execute compile
    package = compiler.compile(mission=mission, base_path=base_dir)
    
    # 1. Assert Context Selector loaded details from WORKSPACE.yaml and PROJECT_STATE.yaml
    assert package.relevant_context["framework"] == "fastapi"
    assert package.relevant_context["language"] == "python"
    assert package.relevant_context["repository_name"] == "MeetingIntelligence"
    
    # 2. Assert Rule Selector warning (since AGENTS.md doesn't exist/empty)
    assert "No matching engineering rules found." in package.warnings
    
    # 3. Assert Reference Collector auto-appended standard config files
    assert any("README.md" in ref for ref in package.relevant_references)
    assert any("pyproject.toml" in ref for ref in package.relevant_references)
    
    # 4. Assert Acceptance Criteria dynamic formatting
    assert "Database Report created" in package.acceptance_criteria
    assert "Code Implementation integrated and verified" in package.acceptance_criteria
    
    # 5. Assert Metadata details
    assert package.package["workspace"] is not None
    assert package.package["compiler_version"] == "1.3.0"  # Read from pyproject.toml version helper fallback
    assert package.package["generated_at"] is not None
