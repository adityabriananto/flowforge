import pytest
import uuid
from flowforge.domain.mission import Mission, MissionState, VALID_STATES
from flowforge.ports.mission_repository import MissionRepository
from flowforge.adapters.mission.in_memory_mission_repository import InMemoryMissionRepository
from flowforge.services.mission_loader import MissionLoader
from flowforge.services.mission_service import MissionService

def test_mission_domain_model_and_enum():
    mission_id = uuid.uuid4()
    mission = Mission(
        id=mission_id,
        title="Test Mission",
        description="Verify domain model works",
        status=MissionState.BACKLOG,
        version="1",
        priority="high",
        goals=["Goal 1"],
        metadata={"priority": "low"}
    )
    assert mission.id == mission_id
    assert mission.title == "Test Mission"
    # Test Enum equality and string equivalence
    assert mission.status == MissionState.BACKLOG
    assert mission.status == "BACKLOG"
    assert "Goal 1" in mission.goals
    assert mission.version == "1"
    assert mission.priority == "high"

def test_mission_loader_from_yaml_valid_v1():
    yaml_content = """
version: "1"
id: "550e8400-e29b-41d4-a716-446655440000"
title: "Parse YAML Test"
description: "Ensure loader successfully parses valid YAML"
status: "READY"
priority: "critical"
owner: "alice"
reviewer: "bob"
phase: "alpha"
goal: "verify v1"
deliverables:
  - "deliverable 1"
constraints:
  - "constraint 1"
definition_of_done:
  - "done 1"
references:
  - "ref 1"
metadata:
  priority: "high"
"""
    # Clear global duplicate cache for test execution independence
    MissionLoader.clear_global_ids()
    
    mission = MissionLoader.load_from_yaml(yaml_content)
    assert mission.title == "Parse YAML Test"
    assert mission.status == MissionState.READY
    assert mission.status == "READY"
    assert mission.priority == "critical"
    assert mission.owner == "alice"
    assert mission.reviewer == "bob"
    assert mission.phase == "alpha"
    assert "deliverable 1" in mission.deliverables
    assert "constraint 1" in mission.constraints
    assert "done 1" in mission.definition_of_done
    assert "ref 1" in mission.references
    assert str(mission.id) == "550e8400-e29b-41d4-a716-446655440000"

def test_mission_loader_invalid_status():
    yaml_content = """
version: "1"
title: "Invalid Status Test"
status: "RUNNING"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Invalid status" in str(exc.value)

def test_mission_loader_invalid_priority():
    yaml_content = """
version: "1"
title: "Invalid Priority Test"
status: "READY"
priority: "super-high"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Invalid priority" in str(exc.value)

def test_mission_loader_unsupported_version():
    yaml_content = """
version: "2"
title: "Unsupported Version Test"
status: "READY"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Unsupported schema version" in str(exc.value)

def test_mission_loader_missing_required_title():
    yaml_content = """
version: "1"
status: "BACKLOG"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Mission title is required" in str(exc.value)

def test_mission_loader_missing_required_version():
    yaml_content = """
title: "Missing Version"
status: "BACKLOG"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Mission schema version is required" in str(exc.value)

def test_mission_loader_invalid_yaml_syntax():
    yaml_content = """
version: "1"
title: "Bad YAML
status: BACKLOG
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Invalid YAML format" in str(exc.value)

def test_mission_loader_duplicate_ids():
    yaml_content_1 = """
version: "1"
id: "550e8400-e29b-41d4-a716-446655441111"
title: "First Mission"
status: "BACKLOG"
"""
    yaml_content_2 = """
version: "1"
id: "550e8400-e29b-41d4-a716-446655441111"
title: "Second Mission with duplicate ID"
status: "BACKLOG"
"""
    MissionLoader.clear_global_ids()
    
    # Loader instance 1
    loader1 = MissionLoader()
    loader1.load(yaml_content_1)
    
    # Try loading duplicate with same loader instance
    with pytest.raises(ValueError) as exc:
        loader1.load(yaml_content_2)
    assert "Duplicate mission ID detected" in str(exc.value)

    # Try loading duplicate with new loader instance (detects globally)
    loader2 = MissionLoader()
    with pytest.raises(ValueError) as exc:
        loader2.load(yaml_content_2)
    assert "Duplicate mission ID detected" in str(exc.value)

@pytest.mark.asyncio
async def test_mission_service_lifecycle_with_enum():
    repo = InMemoryMissionRepository()
    service = MissionService(repo)

    # 1. Create Mission
    mission = await service.create_mission(
        title="Service Test",
        description="Validate business layer logic",
        goals=["Goal 1", "Goal 2"],
        metadata={"team": "qa"},
        priority="low"
    )
    assert mission.status == MissionState.BACKLOG
    assert mission.status == "BACKLOG"
    assert mission.priority == "low"
    
    # Verify save
    saved = await service.get_mission(mission.id)
    assert saved is not None
    assert saved.title == "Service Test"

    # 2. Update Status using string and enum
    updated = await service.update_status(mission.id, "ACTIVE")
    assert updated.status == MissionState.ACTIVE

    updated_enum = await service.update_status(mission.id, MissionState.REVIEW)
    assert updated_enum.status == MissionState.REVIEW
    
    # 3. Invalid Status Update
    with pytest.raises(ValueError) as exc:
        await service.update_status(mission.id, "INVALID_STATE")
    assert "Invalid status" in str(exc.value)

    # 4. List Missions
    missions = await service.list_missions()
    assert len(missions) == 1
    assert missions[0].id == mission.id

    # 5. Delete Mission
    await service.delete_mission(mission.id)
    deleted = await service.get_mission(mission.id)
    assert deleted is None
