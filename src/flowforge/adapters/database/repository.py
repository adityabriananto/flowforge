from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from flowforge.ports.database import DatabaseRepository
from flowforge.domain.models import Workflow, WorkflowInstance, Job, Event
from flowforge.adapters.database.db_models import WorkflowDB, WorkflowInstanceDB, JobDB, EventDB

class SQLAlchemyRepository(DatabaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_workflow(self, workflow: Workflow) -> None:
        db_workflow = WorkflowDB.from_domain(workflow)
        await self.session.merge(db_workflow)

    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        result = await self.session.execute(
            select(WorkflowDB).where(WorkflowDB.id == workflow_id)
        )
        db_workflow = result.scalar_one_or_none()
        return db_workflow.to_domain() if db_workflow else None

    async def save_instance(self, instance: WorkflowInstance) -> None:
        db_instance = WorkflowInstanceDB.from_domain(instance)
        await self.session.merge(db_instance)

    async def get_instance(self, instance_id: uuid.UUID) -> Optional[WorkflowInstance]:
        result = await self.session.execute(
            select(WorkflowInstanceDB).where(WorkflowInstanceDB.id == instance_id)
        )
        db_instance = result.scalar_one_or_none()
        return db_instance.to_domain() if db_instance else None

    async def save_job(self, job: Job) -> None:
        db_job = JobDB.from_domain(job)
        await self.session.merge(db_job)

    async def get_job(self, job_id: uuid.UUID) -> Optional[Job]:
        result = await self.session.execute(
            select(JobDB).where(JobDB.id == job_id)
        )
        db_job = result.scalar_one_or_none()
        return db_job.to_domain() if db_job else None

    async def save_event(self, event: Event) -> None:
        db_event = EventDB.from_domain(event)
        await self.session.merge(db_event)

    async def get_events_for_instance(self, instance_id: uuid.UUID) -> List[Event]:
        result = await self.session.execute(
            select(EventDB).where(EventDB.instance_id == instance_id).order_by(EventDB.timestamp.asc())
        )
        db_events = result.scalars().all()
        return [db_event.to_domain() for db_event in db_events]
