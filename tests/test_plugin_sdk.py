import sys
import os
import uuid
import pytest

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.domain.base_plugin import FlowForgePlugin
from flowforge.domain.plugin_manager import PluginManager
from flowforge.domain.models import WorkflowInstance, Job, Event

# Mock Plugin 1: Audit Logger Plugin for tracking hook execution
class MockAuditPlugin(FlowForgePlugin):
    def __init__(self):
        self.pre_called = False
        self.post_called = False
        self.start_called = False
        self.end_called = False

    async def pre_transition(self, instance: WorkflowInstance, event: str) -> None:
        self.pre_called = True

    async def post_transition(self, instance: WorkflowInstance, event: Event) -> None:
        self.post_called = True

    async def on_worker_start(self, job: Job) -> None:
        self.start_called = True

    async def on_worker_end(self, job: Job) -> None:
        self.end_called = True

# Mock Plugin 2: Blocker Plugin to verify abort behavior
class TransitionBlockerPlugin(FlowForgePlugin):
    async def pre_transition(self, instance: WorkflowInstance, event: str) -> None:
        if event == "START":
            raise PermissionError("Transition blocked by BlockerPlugin")

# Mock Plugin 3: Faulty Plugin that raises error in post_transition
class FaultyPlugin(FlowForgePlugin):
    async def post_transition(self, instance: WorkflowInstance, event: Event) -> None:
        raise RuntimeError("Something failed in post transition")


@pytest.mark.asyncio
async def test_plugin_lifecycle_hooks_called():
    manager = PluginManager()
    audit_plugin = MockAuditPlugin()
    
    manager.register_plugin(audit_plugin)
    
    instance = WorkflowInstance(id=uuid.uuid4(), workflow_id=uuid.uuid4(), current_state="IDLE")
    job = Job(id=uuid.uuid4(), instance_id=instance.id, state_name="CODING", status="PENDING")
    event = Event(id=uuid.uuid4(), instance_id=instance.id, event_type="STATE_CHANGED", payload={}, triggered_by="SYSTEM")

    # 1. Trigger transition hooks
    await manager.trigger_pre_transition(instance, "START")
    await manager.trigger_post_transition(instance, event)
    
    assert audit_plugin.pre_called is True
    assert audit_plugin.post_called is True

    # 2. Trigger worker hooks
    await manager.trigger_on_worker_start(job)
    await manager.trigger_on_worker_end(job)
    
    assert audit_plugin.start_called is True
    assert audit_plugin.end_called is True

@pytest.mark.asyncio
async def test_pre_transition_aborts():
    manager = PluginManager()
    blocker = TransitionBlockerPlugin()
    manager.register_plugin(blocker)

    instance = WorkflowInstance(id=uuid.uuid4(), workflow_id=uuid.uuid4(), current_state="IDLE")

    # pre_transition is expected to propagate error and raise PermissionError
    with pytest.raises(PermissionError) as exc_info:
        await manager.trigger_pre_transition(instance, "START")
        
    assert "blocked by BlockerPlugin" in str(exc_info.value)

@pytest.mark.asyncio
async def test_post_transition_error_isolated():
    manager = PluginManager()
    faulty = FaultyPlugin()
    audit = MockAuditPlugin()
    
    # Register faulty plugin first, then audit plugin
    manager.register_plugin(faulty)
    manager.register_plugin(audit)

    instance = WorkflowInstance(id=uuid.uuid4(), workflow_id=uuid.uuid4(), current_state="IDLE")
    event = Event(id=uuid.uuid4(), instance_id=instance.id, event_type="STATE_CHANGED", payload={}, triggered_by="SYSTEM")

    # Even though FaultyPlugin raises an exception in post_transition, 
    # it should be caught and logged, allowing AuditPlugin to execute successfully.
    await manager.trigger_post_transition(instance, event)
    
    assert audit.post_called is True
