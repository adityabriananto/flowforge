import sys
import os
import uuid
import pytest

# Add src/ folder to sys.path to allow imports in testing environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.domain.models import Workflow, StateConfig, WorkflowInstance
from flowforge.domain.engine import StateMachine, InvalidTransitionError

@pytest.fixture
def sample_workflow():
    # Setup States configuration matching the PRD specification
    states = {
        "IDLE": StateConfig(name="IDLE", next_state="CODING"),
        "CODING": StateConfig(name="CODING", worker_type="python_agent", script="agents/coder.py", next_state="TESTING", on_failure="FAILED"),
        "TESTING": StateConfig(name="TESTING", worker_type="pytest_runner", script="agents/tester.py", next_state="AWAITING_APPROVAL", on_failure="CODING"),
        "AWAITING_APPROVAL": StateConfig(name="AWAITING_APPROVAL", require_human=True, on_approve="COMPLETED", on_reject="CODING"),
        "COMPLETED": StateConfig(name="COMPLETED", is_final=True),
        "FAILED": StateConfig(name="FAILED", is_final=True)
    }
    
    return Workflow(
        id=uuid.uuid4(),
        name="Test Workflow",
        version="1.0.0",
        initial_state="IDLE",
        states=states
    )

@pytest.fixture
def workflow_instance(sample_workflow):
    return WorkflowInstance(
        id=uuid.uuid4(),
        workflow_id=sample_workflow.id,
        current_state="IDLE"
    )

def test_initial_transition(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    
    # Transition from IDLE to CODING using START event
    event = engine.transition(workflow_instance, "START")
    
    assert workflow_instance.current_state == "CODING"
    assert event.event_type == "STATE_CHANGED"
    assert event.payload["from_state"] == "IDLE"
    assert event.payload["to_state"] == "CODING"
    assert event.payload["trigger_event"] == "START"

def test_success_transition_flow(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    
    # IDLE -> CODING
    engine.transition(workflow_instance, "START")
    # CODING -> TESTING
    engine.transition(workflow_instance, "SUCCESS")
    assert workflow_instance.current_state == "TESTING"
    
    # TESTING -> AWAITING_APPROVAL
    event = engine.transition(workflow_instance, "SUCCESS")
    assert workflow_instance.current_state == "AWAITING_APPROVAL"
    assert event.event_type == "HITL_AWAITING"
    assert event.payload["require_human"] is True

def test_hitl_approval_and_completion(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    workflow_instance.current_state = "AWAITING_APPROVAL"
    
    # Approve HITL state
    event = engine.transition(workflow_instance, "APPROVE")
    assert workflow_instance.current_state == "COMPLETED"
    assert event.event_type == "STATE_CHANGED"
    assert event.payload["to_state"] == "COMPLETED"

def test_hitl_rejection_loops_back(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    workflow_instance.current_state = "AWAITING_APPROVAL"
    
    # Reject HITL state, should loop back to CODING
    event = engine.transition(workflow_instance, "REJECT")
    assert workflow_instance.current_state == "CODING"
    assert event.payload["to_state"] == "CODING"

def test_testing_failure_loops_back(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    workflow_instance.current_state = "TESTING"
    
    # TESTING fails, should go back to CODING
    event = engine.transition(workflow_instance, "FAILURE")
    assert workflow_instance.current_state == "CODING"
    assert event.payload["to_state"] == "CODING"

def test_invalid_transition_throws_error(sample_workflow, workflow_instance):
    engine = StateMachine(sample_workflow)
    
    # Cannot call APPROVE while in IDLE state
    with pytest.raises(InvalidTransitionError) as exc_info:
        engine.transition(workflow_instance, "APPROVE")
    
    assert exc_info.value.current_state == "IDLE"
    assert exc_info.value.event == "APPROVE"
