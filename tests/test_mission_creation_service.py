import pytest
import os
import asyncio
from unittest.mock import MagicMock, patch
from flowforge.services.mission_creation_service import MissionCreationService
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.adapters.mission.in_memory_mission_repository import InMemoryMissionRepository
from flowforge.domain.mission_draft import MissionReviewAction

@pytest.mark.asyncio
async def test_mission_creation_service_accept(tmp_path):
    base = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base)
    
    repo = InMemoryMissionRepository()
    
    mock_review = MagicMock()
    mock_review.review_mission.return_value = MissionReviewAction.ACCEPT
    
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
    assert mission.code == "PROJECT-000"
    
    saved = await repo.get(mission.id)
    assert saved is not None

@pytest.mark.asyncio
async def test_mission_creation_service_cancel(tmp_path):
    base = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base)
    
    repo = InMemoryMissionRepository()
    
    mock_review = MagicMock()
    mock_review.review_mission.return_value = MissionReviewAction.CANCEL
    
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
    
    all_missions = await repo.list_all()
    assert len(all_missions) == 0

@pytest.mark.asyncio
async def test_mission_creation_service_interactive_edit(tmp_path):
    base = str(tmp_path)
    EngineeringWorkspace.initialize_workspace(base)
    
    repo = InMemoryMissionRepository()
    
    mock_review = MagicMock()
    mock_review.review_mission.side_effect = [MissionReviewAction.EDIT, MissionReviewAction.ACCEPT]
    
    service = MissionCreationService(
        repository=repo,
        base_path=base,
        review_service=mock_review
    )
    
    # We'll patch _prompt_input to automatically provide values during the EDIT phase
    def mock_prompt(prompt_text, current_val):
        if "Title" in prompt_text:
            return "Edited Title"
        if "Goal" in prompt_text:
            return "Edited Goal"
        if "Priority" in prompt_text:
            return "medium"
        return "Unknown"
        
    with patch.object(service, '_prompt_input', side_effect=mock_prompt):
        mission = await service.create_mission(
            title="Old Title",
            goal="Old Goal",
            priority="high"
        )
        
    assert mission is not None
    assert mission.title == "Edited Title"
    assert mission.goal == "Edited Goal"
    assert mission.priority == "medium"
    assert mock_review.review_mission.call_count == 2
