import pytest
from flowforge.services.planning_context_builder import PlanningContext
from flowforge.services.mission_planning_engine import MissionPlanningEngine
from flowforge.domain.mission_draft import DeveloperInput

def test_generate_draft_deterministic_backend():
    engine = MissionPlanningEngine()
    context = PlanningContext(
        framework="fastapi",
        language="python",
        project_type="backend",
        recent_adrs=["adr-001"],
        recent_rfcs=[]
    )
    
    dev_input = DeveloperInput(
        title="Implement User Auth",
        business_goal="Add JWT authentication",
        priority="high"
    )

    mission = engine.generate_draft(
        context=context,
        developer_input=dev_input,
        code="PROJECT-001",
        notes="Use PyJWT"
    )
    
    assert mission.title == "Implement User Auth"
    assert mission.goal == "Add JWT authentication"
    assert mission.code == "PROJECT-001"
    assert mission.priority == "high"
    assert mission.metadata["developer_notes"] == "Use PyJWT"
    assert mission.metadata["project_type"] == "backend"
    
    # Check deliverables
    assert any("API endpoints" in d for d in mission.deliverables)
    assert any("JWT" in d for d in mission.deliverables)
    
    # Check constraints
    assert any("python" in c.lower() for c in mission.constraints)
    assert any("fastapi" in c.lower() for c in mission.constraints)
    
    # Check DoD
    assert any("100%" in dod for dod in mission.definition_of_done)
    
    # Check references
    assert "adr-001" in mission.references

def test_generate_draft_deterministic_frontend():
    engine = MissionPlanningEngine()
    context = PlanningContext(
        framework="react",
        language="typescript",
        project_type="frontend"
    )
    
    dev_input = DeveloperInput(
        title="Build Login Page",
        business_goal="Create responsive login UI",
        priority="medium"
    )

    mission = engine.generate_draft(
        context=context,
        developer_input=dev_input,
        code="PROJECT-002"
    )
    
    assert mission.metadata["project_type"] == "frontend"
    assert any("UI components" in d for d in mission.deliverables)
    assert any("react" in c.lower() for c in mission.constraints)
