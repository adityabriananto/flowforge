from datetime import datetime, timezone
import json
from typing import Dict, Any, Optional
import uuid
from sqlalchemy import String, TEXT, JSON, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flowforge.adapters.database.database import Base
from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig, Job, Event

class WorkflowDB(Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(50))
    initial_state: Mapped[str] = mapped_column(String(100))
    definition_json: Mapped[str] = mapped_column(TEXT)  # JSON string of States config
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    instances = relationship("WorkflowInstanceDB", back_populates="workflow", cascade="all, delete-orphan")

    def to_domain(self) -> Workflow:
        states_dict = json.loads(self.definition_json)
        states = {}
        for state_name, config in states_dict.items():
            states[state_name] = StateConfig(**config)
            
        return Workflow(
            id=self.id,
            name=self.name,
            version=self.version,
            initial_state=self.initial_state,
            states=states,
            created_at=self.created_at
        )

    @staticmethod
    def from_domain(workflow: Workflow) -> "WorkflowDB":
        states_serialized = {
            name: {
                "name": config.name,
                "worker_type": config.worker_type,
                "script": config.script,
                "timeout_seconds": config.timeout_seconds,
                "next_state": config.next_state,
                "on_failure": config.on_failure,
                "require_human": config.require_human,
                "on_approve": config.on_approve,
                "on_reject": config.on_reject,
                "is_final": config.is_final
            }
            for name, config in workflow.states.items()
        }
        
        return WorkflowDB(
            id=workflow.id,
            name=workflow.name,
            version=workflow.version,
            initial_state=workflow.initial_state,
            definition_json=json.dumps(states_serialized),
            created_at=workflow.created_at
        )


class WorkflowInstanceDB(Base):
    __tablename__ = "workflow_instances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"))
    current_state: Mapped[str] = mapped_column(String(100))
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    workflow = relationship("WorkflowDB", back_populates="instances")
    jobs = relationship("JobDB", back_populates="instance", cascade="all, delete-orphan")

    def to_domain(self) -> WorkflowInstance:
        return WorkflowInstance(
            id=self.id,
            workflow_id=self.workflow_id,
            current_state=self.current_state,
            variables=self.variables,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_domain(instance: WorkflowInstance) -> "WorkflowInstanceDB":
        return WorkflowInstanceDB(
            id=instance.id,
            workflow_id=instance.workflow_id,
            current_state=instance.current_state,
            variables=instance.variables,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )


class JobDB(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    state_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))  # PENDING, RUNNING, COMPLETED, FAILED
    stdout: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    stderr: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    instance = relationship("WorkflowInstanceDB", back_populates="jobs")

    def to_domain(self) -> Job:
        return Job(
            id=self.id,
            instance_id=self.instance_id,
            state_name=self.state_name,
            status=self.status,
            stdout=self.stdout,
            stderr=self.stderr,
            started_at=self.started_at,
            ended_at=self.ended_at
        )

    @staticmethod
    def from_domain(job: Job) -> "JobDB":
        return JobDB(
            id=job.id,
            instance_id=job.instance_id,
            state_name=job.state_name,
            status=job.status,
            stdout=job.stdout,
            stderr=job.stderr,
            started_at=job.started_at,
            ended_at=job.ended_at
        )


class EventDB(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    triggered_by: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_domain(self) -> Event:
        return Event(
            id=self.id,
            instance_id=self.instance_id,
            event_type=self.event_type,
            payload=self.payload,
            triggered_by=self.triggered_by,
            timestamp=self.timestamp
        )

    @staticmethod
    def from_domain(event: Event) -> "EventDB":
        return EventDB(
            id=event.id,
            instance_id=event.instance_id,
            event_type=event.event_type,
            payload=event.payload,
            triggered_by=event.triggered_by,
            timestamp=event.timestamp
        )
