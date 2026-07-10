import pytest
import uuid
from flowforge.domain.mission import Mission
from flowforge.ports.mission_repository import MissionRepository
from flowforge.adapters.mission.in_memory_mission_repository import InMemoryMissionRepository
from flowforge.services.mission_loader import MissionLoader
from flowforge.services.mission_service import MissionService

def test_mission_domain_model():
    mission_id = uuid.uuid4()
    mission = Mission(
        id=mission_id,
        title="Test Mission",
        description="Verify domain model works",
        status="BACKLOG",
        goals=["Goal 1"],
        metadata={"priority": "low"}
    )
    assert mission.id == mission_id
    assert mission.title == "Test Mission"
    assert mission.status == "BACKLOG"
    assert "Goal 1" in mission.goals

def test_mission_loader_from_yaml():
    yaml_content = """
title: "Parse YAML Test"
description: "Ensure loader successfully parses valid YAML"
status: "READY"
goals:
  - "Goal A"
metadata:
  priority: "high"
"""
    mission = MissionLoader.load_from_yaml(yaml_content)
    assert mission.title == "Parse YAML Test"
    assert mission.status == "READY"
    assert "Goal A" in mission.goals
    assert mission.metadata.get("priority") == "high"
    assert isinstance(mission.id, uuid.UUID)

def test_mission_loader_invalid_status():
    yaml_content = """
title: "Invalid Status Test"
status: "RUNNING"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Invalid status" in str(exc.value)

def test_mission_loader_missing_title():
    yaml_content = """
status: "BACKLOG"
"""
    with pytest.raises(ValueError) as exc:
        MissionLoader.load_from_yaml(yaml_content)
    assert "Mission title is required" in str(exc.value)

@pytest.mark.asyncio
async def test_mission_service_lifecycle():
    repo = InMemoryMissionRepository()
    service = MissionService(repo)

    # 1. Create Mission
    mission = await service.create_mission(
        title="Service Test",
        description="Validate business layer logic",
        goals=["Goal 1", "Goal 2"],
        metadata={"team": "qa"}
    )
    assert mission.status == "BACKLOG"
    
    # Verify save
    saved = await service.get_mission(mission.id)
    assert saved is not None
    assert saved.title == "Service Test"

    # 2. Update Status
    updated = await service.update_status(mission.id, "ACTIVE")
    assert updated.status == "ACTIVE"
    
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
