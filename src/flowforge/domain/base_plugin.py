from abc import ABC
from flowforge.domain.models import WorkflowInstance, Job, Event

class FlowForgePlugin(ABC):
    """
    Base class that all FlowForge plugins must inherit from.
    Provides async lifecycle hooks that can be overridden by plugins.
    """
    
    async def pre_transition(self, instance: WorkflowInstance, event: str) -> None:
        """Called asynchronously before a state transition is executed."""
        pass

    async def post_transition(self, instance: WorkflowInstance, event: Event) -> None:
        """Called asynchronously after a state transition has completed."""
        pass

    async def on_worker_start(self, job: Job) -> None:
        """Called asynchronously before a worker job execution starts."""
        pass

    async def on_worker_end(self, job: Job) -> None:
        """Called asynchronously after a worker job execution ends."""
        pass
