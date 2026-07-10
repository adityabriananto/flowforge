import pytest
import os
from flowforge.domain.agent_profile import AgentProfile, VALID_EXECUTION_MODES
from flowforge.ports.agent_profile_repository import AgentProfileRepository
from flowforge.adapters.agent_profile.in_memory_agent_profile_repository import InMemoryAgentProfileRepository
from flowforge.services.agent_profile_loader import AgentProfileLoader
from flowforge.services.agent_profile_service import AgentProfileService

def test_agent_profile_domain_model():
    profile = AgentProfile(
        id="test-agent",
        display_name="Test Agent",
        version="1",
        provider="custom",
        capabilities={"coding": 80, "review": 70},
        execution_mode="api",
        context_limit=4096
    )
    assert profile.id == "test-agent"
    assert profile.capabilities.get("coding") == 80
    assert profile.execution_mode == "api"

def test_agent_profile_loader_valid_yaml():
    yaml_content = """
version: "1"
id: "claude-3-5"
display_name: "Claude 3.5 Sonnet Agent"
provider: "anthropic"
execution_mode: "api"
capabilities:
  coding: 95
  refactoring: 90
limitations:
  - "no-internet"
context_limit: 200000
"""
    AgentProfileLoader.clear_global_ids()
    profile = AgentProfileLoader.load_from_yaml(yaml_content)
    assert profile.id == "claude-3-5"
    assert profile.display_name == "Claude 3.5 Sonnet Agent"
    assert profile.capabilities["coding"] == 95
    assert profile.execution_mode == "api"

def test_agent_profile_loader_missing_required_fields():
    yaml_content = """
version: "1"
id: "claude-3-5"
display_name: "Claude 3.5 Sonnet Agent"
provider: "anthropic"
capabilities:
  coding: 95
"""
    # missing execution_mode
    with pytest.raises(ValueError) as exc:
        AgentProfileLoader.load_from_yaml(yaml_content)
    assert "Required field 'execution_mode' is missing" in str(exc.value)

def test_agent_profile_loader_invalid_version():
    yaml_content = """
version: "2"
id: "claude-3-5"
display_name: "Claude 3.5 Sonnet Agent"
provider: "anthropic"
execution_mode: "api"
capabilities:
  coding: 95
"""
    with pytest.raises(ValueError) as exc:
        AgentProfileLoader.load_from_yaml(yaml_content)
    assert "Unsupported schema version" in str(exc.value)

def test_agent_profile_loader_invalid_execution_mode():
    yaml_content = """
version: "1"
id: "claude-invalid-mode"
display_name: "Claude 3.5 Sonnet Agent"
provider: "anthropic"
execution_mode: "cloud"
capabilities:
  coding: 95
"""
    AgentProfileLoader.clear_global_ids()
    with pytest.raises(ValueError) as exc:
        AgentProfileLoader.load_from_yaml(yaml_content)
    assert "Invalid execution mode" in str(exc.value)

def test_agent_profile_loader_invalid_capability_score():
    yaml_content = """
version: "1"
id: "claude-invalid-score"
display_name: "Claude 3.5 Sonnet Agent"
provider: "anthropic"
execution_mode: "api"
capabilities:
  coding: 150
"""
    AgentProfileLoader.clear_global_ids()
    with pytest.raises(ValueError) as exc:
        AgentProfileLoader.load_from_yaml(yaml_content)
    assert "Capability score for 'coding' must be between 0 and 100" in str(exc.value)

def test_agent_profile_loader_duplicate_ids():
    yaml_content1 = """
version: "1"
id: "duplicate-id"
display_name: "Agent 1"
provider: "vendor"
execution_mode: "api"
capabilities:
  coding: 50
"""
    yaml_content2 = """
version: "1"
id: "duplicate-id"
display_name: "Agent 2"
provider: "vendor"
execution_mode: "api"
capabilities:
  coding: 50
"""
    AgentProfileLoader.clear_global_ids()
    loader = AgentProfileLoader()
    loader.load(yaml_content1)

    with pytest.raises(ValueError) as exc:
        loader.load(yaml_content2)
    assert "Duplicate agent profile ID detected" in str(exc.value)

def test_load_sample_profiles_directory():
    # Verify that all YAML files in agent_profiles/ can be successfully parsed
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    profiles_dir = os.path.join(root_dir, "agent_profiles")
    
    assert os.path.exists(profiles_dir)
    yaml_files = [f for f in os.listdir(profiles_dir) if f.endswith(".yaml")]
    assert len(yaml_files) == 6  # cursor-free, cursor-pro, claude, codex, gemini, qwen
    
    AgentProfileLoader.clear_global_ids()
    loader = AgentProfileLoader()
    for file_name in yaml_files:
        file_path = os.path.join(profiles_dir, file_name)
        profile = loader.load_from_file(file_path)
        assert profile.id is not None
        assert profile.display_name is not None

@pytest.mark.asyncio
async def test_agent_profile_service_filtering():
    repo = InMemoryAgentProfileRepository()
    service = AgentProfileService(repo)

    profile_low = AgentProfile(
        id="low-agent", display_name="Low Agent", version="1", provider="v",
        capabilities={"coding": 40}, execution_mode="api"
    )
    profile_medium = AgentProfile(
        id="medium-agent", display_name="Medium Agent", version="1", provider="v",
        capabilities={"coding": 70}, execution_mode="api"
    )
    profile_high = AgentProfile(
        id="high-agent", display_name="High Agent", version="1", provider="v",
        capabilities={"coding": 95}, execution_mode="api"
    )

    await service.save_profile(profile_low)
    await service.save_profile(profile_medium)
    await service.save_profile(profile_high)

    # Find profiles with coding >= 50, sorted descending
    matches = await service.find_profiles_by_capability("coding", 50)
    assert len(matches) == 2
    assert matches[0].id == "high-agent"
    assert matches[1].id == "medium-agent"
