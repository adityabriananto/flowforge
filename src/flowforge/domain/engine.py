from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig, Event

class InvalidTransitionError(Exception):
    """Exception raised when an invalid state transition is attempted."""
    def __init__(self, current_state: str, event: str, message: str = ""):
        self.current_state = current_state
        self.event = event
        self.message = message or f"Transition from state '{current_state}' via event '{event}' is invalid."
        super().__init__(self.message)

class StateMachine:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        # Load transitions table, construct from StateConfig if empty (backward compatibility)
        self.transitions = dict(getattr(workflow, "transitions", {}))
        if not self.transitions:
            for state_name, config in workflow.states.items():
                if not config.require_human:
                    if config.next_state:
                        self.transitions[(state_name, "SUCCESS")] = config.next_state
                        if state_name == workflow.initial_state:
                            self.transitions[(state_name, "START")] = config.next_state
                    if config.on_failure:
                        self.transitions[(state_name, "FAILURE")] = config.on_failure
                else:
                    if config.on_approve:
                        self.transitions[(state_name, "APPROVE")] = config.on_approve
                    if config.on_reject:
                        self.transitions[(state_name, "REJECT")] = config.on_reject

    def transition(
        self, 
        instance: WorkflowInstance, 
        event: str, 
        triggered_by: str = "SYSTEM"
    ) -> Event:
        """
        Executes a transition on a WorkflowInstance triggered by an event.
        Returns an Event domain object summarizing the change.
        """
        current_state_name = instance.current_state
        state_config: Optional[StateConfig] = self.workflow.states.get(current_state_name)

        if not state_config:
            raise ValueError(f"Current state '{current_state_name}' does not exist in workflow definition.")

        # Resolve next state using the transition table mapping
        next_state_name = self.transitions.get((current_state_name, event))

        # If no valid next state is found, it's an invalid transition
        if not next_state_name:
            raise InvalidTransitionError(current_state_name, event)

        # Validate that the target state exists
        if next_state_name not in self.workflow.states:
            raise ValueError(f"Target state '{next_state_name}' does not exist in workflow definition.")

        # Update the workflow instance
        old_state = instance.current_state
        instance.current_state = next_state_name
        instance.updated_at = datetime.now(timezone.utc)

        # Create and return transition event
        event_id = uuid.uuid4()
        event_type = "STATE_CHANGED"
        
        target_state_config = self.workflow.states[next_state_name]
        if target_state_config.require_human:
            event_type = "HITL_AWAITING"

        return Event(
            id=event_id,
            instance_id=instance.id,
            event_type=event_type,
            payload={
                "from_state": old_state,
                "to_state": next_state_name,
                "trigger_event": event,
                "require_human": target_state_config.require_human
            },
            triggered_by=triggered_by
        )
