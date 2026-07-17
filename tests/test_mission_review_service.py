import pytest
from flowforge.domain.mission_factory import MissionFactory
from flowforge.services.mission_review_service import MissionReviewService
from flowforge.domain.mission_draft import MissionDraft, DeveloperInput, MissionReviewAction
from flowforge.services.planning_context_builder import PlanningContext

def test_mission_review_accept():
    inputs = ["a"]
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
    
    draft = MissionDraft(
        developer_input=DeveloperInput("Test Mission", "Goal", "Ctx", "Usr", "High"),
        planning_context=PlanningContext(),
        generated_mission=mission
    )
    
    result = service.review_mission(draft)
    assert result == MissionReviewAction.ACCEPT
    
    output_text = "\n".join(outputs)
    assert "Mission Draft" in output_text
    assert "Developer Input" in output_text
    assert "Unknown" in output_text
    assert "  - D1" in output_text
    assert "Expected Engineering Outputs:" in output_text

def test_mission_review_cancel():
    inputs = ["c"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    service = MissionReviewService(input_provider=mock_input, print_provider=lambda x: None)
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    draft = MissionDraft(
        developer_input=DeveloperInput("Test Mission", "Goal", "Ctx", "Usr", "High"),
        planning_context=PlanningContext(),
        generated_mission=mission
    )
    
    result = service.review_mission(draft)
    assert result == MissionReviewAction.CANCEL

def test_mission_review_edit():
    inputs = ["e"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    service = MissionReviewService(input_provider=mock_input, print_provider=lambda x: None)
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    draft = MissionDraft(
        developer_input=DeveloperInput("Test Mission", "Goal", "Ctx", "Usr", "High"),
        planning_context=PlanningContext(),
        generated_mission=mission
    )
    
    result = service.review_mission(draft)
    assert result == MissionReviewAction.EDIT

def test_mission_review_invalid_then_accept():
    inputs = ["invalid", "a"]
    def mock_input(prompt):
        return inputs.pop(0)
        
    outputs = []
    service = MissionReviewService(input_provider=mock_input, print_provider=lambda x: outputs.append(str(x)))
    
    mission = MissionFactory.create(
        title="Test Mission",
        description="Goal",
        code="PROJECT-001"
    )
    draft = MissionDraft(
        developer_input=DeveloperInput("Test Mission", "Goal", "Ctx", "Usr", "High"),
        planning_context=PlanningContext(),
        generated_mission=mission
    )
    
    result = service.review_mission(draft)
    assert result == MissionReviewAction.ACCEPT
    assert any("Please enter 'A', 'E', or 'C'." in o for o in outputs)
