import pytest
import os
import uuid
import yaml
from flowforge.domain.mission import Mission, MissionState
from flowforge.domain.agent_profile import AgentProfile
from flowforge.domain.mission_package import MissionPackage
from flowforge.services.compiler.context_selector import ContextSelector
from flowforge.services.compiler.rule_selector import RuleSelector
from flowforge.services.compiler.reference_collector import ReferenceCollector
from flowforge.services.compiler.compiler import MissionPackageCompiler
from flowforge.services.compiler.renderer import MissionPackageRenderer
from flowforge.entrypoints.cli.main import cmd_compile

def test_context_selector_filtering():
    project_context = {
        "auth_config": "JWT_SECRET=supersecret",
        "database_url": "sqlite:///:memory:",
        "logging_level": "DEBUG"
    }
    keywords = ["auth", "database"]
    
    selected = ContextSelector.select_relevant_context(keywords, project_context)
    assert "auth_config" in selected
    assert "database_url" in selected
    assert "logging_level" not in selected

def test_rule_selector_extraction(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("""
# Rules List
* Always write clean code.
* Ensure database connections are pooled.
* Mask all API keys in logs.
""")
    keywords = ["database", "api"]
    selected = RuleSelector.select_relevant_rules(keywords, str(agents_md))
    assert len(selected) == 2
    assert any("database" in rule for rule in selected)
    assert any("Mask all API keys" in rule for rule in selected)
    assert not any("clean code" in rule for rule in selected)

def test_mission_package_compiler_success(tmp_path):
    mission = Mission(
        id=uuid.uuid4(),
        title="Implement database query optimizer",
        description="Optimize slow read operations",
        status=MissionState.ACTIVE,
        version="1",
        priority="high",
        deliverables=["Query logs", "Index changes"],
        definition_of_done=["Performance gain > 2x"],
        references=["performance_guide"]
    )
    
    agent_profile = AgentProfile(
        id="opt-agent",
        display_name="Optimization Agent",
        version="1",
        provider="local",
        capabilities={"coding": 80},
        limitations=["limited-concurrency"],
        execution_mode="api"
    )

    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("* Ensure database is indexed correctly.\n* Keep code clean.")

    # Create dummy reference doc
    ref_dir = tmp_path / "references"
    os.makedirs(ref_dir, exist_ok=True)
    ref_file = ref_dir / "performance_guide.txt"
    ref_file.write_text("Database indexing is key to query optimization.")

    compiler = MissionPackageCompiler(
        rules_file_path=str(agents_md),
        references_dir=str(ref_dir)
    )

    project_context = {
        "database_schema": "CREATE TABLE users...",
        "unused_var": "val = 1"
    }

    package = compiler.compile(
        mission=mission,
        agent_profile=agent_profile,
        project_context=project_context,
        workflow_state="ACTIVE",
        sprint_status="Sprint 12"
    )

    assert isinstance(package, MissionPackage)
    assert "database query optimizer" in package.mission_summary
    assert "ACTIVE" in package.relevant_context["workflow_state"]
    assert "Sprint 12" in package.relevant_context["sprint_status"]
    assert "database_schema" in package.relevant_context
    assert "unused_var" not in package.relevant_context # Not matching database optimizer keywords
    assert any("limited-concurrency" in constraint for constraint in package.constraints)
    assert any("database is indexed" in rule for rule in package.relevant_rules)
    assert any("performance_guide" in ref for ref in package.relevant_references)
    assert any("Database indexing is key" in ref for ref in package.relevant_references)

def test_renderer_serialization():
    package = MissionPackage(
        mission_summary="Optimize Database",
        objective="Optimize query plan",
        deliverables=["Indexes"],
        constraints=["Max memory 2GB"],
        relevant_rules=["Use proper indexing"],
        relevant_context={"db_engine": "postgres"},
        relevant_references=["[tuning_doc]"],
        acceptance_criteria=["Index built"],
        definition_of_done=["Done"]
    )
    
    yaml_str = MissionPackageRenderer.render_to_yaml(package)
    parsed = yaml.safe_load(yaml_str)
    
    assert parsed["mission_summary"] == "Optimize Database"
    assert parsed["relevant_context"]["db_engine"] == "postgres"
    assert "tuning_doc" in parsed["relevant_references"][0]

def test_cli_compile_command(tmp_path):
    mission_file = tmp_path / "mission.ff.yaml"
    mission_file.write_text("""
version: "1"
id: "550e8400-e29b-41d4-a716-446655442222"
title: "CLI Compile Test"
status: "READY"
priority: "low"
""")
    
    profile_file = tmp_path / "claude.yaml"
    profile_file.write_text("""
version: "1"
id: "claude"
display_name: "Claude"
provider: "anthropic"
execution_mode: "api"
capabilities:
  coding: 90
""")

    class Args:
        def __init__(self, m, p):
            self.mission_file = m
            self.profile = p

    args = Args(str(mission_file), str(profile_file))

    old_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        cmd_compile(args)
        output_pkg = f"mission_package_550e8400-e29b-41d4-a716-446655442222.yaml"
        assert os.path.exists(output_pkg)
        with open(output_pkg, "r") as f:
            data = yaml.safe_load(f.read())
        assert "CLI Compile Test" in data["mission_summary"]
    finally:
        os.chdir(old_cwd)
