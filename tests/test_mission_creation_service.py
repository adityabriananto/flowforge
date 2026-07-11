import pytest
import os
import asyncio
from unittest.mock import MagicMock
from flowforge.services.mission_creation_service import MissionCreationService
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.adapters.mission.in_memory_mission_repository import InMemoryMissionRepository

@pytest.mark.asyncio
async def test_mission_creation_service_accept(tmp_path):
    base = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base)
    
    repo = InMemoryMissionRepository()
    
    # Mock ReviewService to automatically accept
    mock_review = MagicMock()
    mock_review.review_mission.return_value = True
    
    service = MissionCreationService(
        repository=repo,
        base_path=base,
        review_service=mock_review
    )
    
    mission = await service.create_mission(
        title="Test Mission",
        goal="Do something",
        priority="high"
    )
    
    assert mission is not None
    assert mission.title == "Test Mission"
    assert mission.code == "PROJECT-000" # Assuming empty repo generates PROJECT-000
    
    # Verify persistence
    saved = await repo.get(mission.id)
    assert saved is not None

@pytest.mark.asyncio
async def test_mission_creation_service_reject(tmp_path):
    base = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base)
    
    repo = InMemoryMissionRepository()
    
    # Mock ReviewService to automatically reject
    mock_review = MagicMock()
    mock_review.review_mission.return_value = False
    
    service = MissionCreationService(
        repository=repo,
        base_path=base,
        review_service=mock_review
    )
    
    mission = await service.create_mission(
        title="Test Mission",
        goal="Do something",
        priority="high"
    )
    
    assert mission is None
    
    # Verify nothing was persisted
    all_missions = await repo.list_all()
    assert len(all_missions) == 0
