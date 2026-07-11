import pytest
from flowforge.domain.mission_factory import MissionFactory
from flowforge.services.mission_review_service import MissionReviewService

def test_mission_review_accept():
    # Mock input to return 'y'
    inputs = ["y"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    outputs = []
    def mock_print(msg):
        outputs.append(str(msg))
        
    service = MissionReviewService(input_provider=mock_input, print_provider=mock_print)
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    mission.deliverables = ["D1"]
    
    result = service.review_mission(mission)
    assert result is True
    
    output_text = "\n".join(outputs)
    assert "MISSION DRAFT REVIEW" in output_text
    assert "PROJECT-001" in output_text
    assert "D1" in output_text

def test_mission_review_reject():
    inputs = ["n"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    service = MissionReviewService(input_provider=mock_input, print_provider=lambda x: None)
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    
    result = service.review_mission(mission)
    assert result is False

def test_mission_review_invalid_then_accept():
    inputs = ["invalid", "y"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    outputs = []
    service = MissionReviewService(input_provider=mock_input, print_provider=lambda x: outputs.append(str(x)))
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    
    result = service.review_mission(mission)
    assert result is True
    assert any("Please enter 'y' or 'n'" in msg for msg in outputs)
