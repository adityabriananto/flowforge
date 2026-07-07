from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from flowforge.domain.models import Workflow, WorkflowInstance, Job, Event

class DatabaseRepository(ABC):
    @abstractmethod
    async def save_workflow(self, workflow: Workflow) -> None:
        pass

    @abstractmethod
    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        pass

    @abstractmethod
    async def save_instance(self, instance: WorkflowInstance) -> None:
        pass

    @abstractmethod
    async def get_instance(self, instance_id: uuid.UUID) -> Optional[WorkflowInstance]:
        pass

    @abstractmethod
    async def save_job(self, job: Job) -> None:
        pass

    @abstractmethod
    async def get_job(self, job_id: uuid.UUID) -> Optional[Job]:
        pass

    @abstractmethod
    async def save_event(self, event: Event) -> None:
        pass

    @abstractmethod
    async def get_events_for_instance(self, instance_id: uuid.UUID) -> List[Event]:
        pass
