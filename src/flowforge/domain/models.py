from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

@dataclass
class StateConfig:
    name: str
    worker_type: Optional[str] = None
    script: Optional[str] = None
    timeout_seconds: int = 300
    next_state: Optional[str] = None
    on_failure: Optional[str] = None
    require_human: bool = False
    on_approve: Optional[str] = None
    on_reject: Optional[str] = None
    is_final: bool = False

@dataclass
class Workflow:
    id: uuid.UUID
    name: str
    version: str
    initial_state: str
    states: Dict[str, StateConfig]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class WorkflowInstance:
    id: uuid.UUID
    workflow_id: uuid.UUID
    current_state: str
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Job:
    id: uuid.UUID
    instance_id: uuid.UUID
    state_name: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

@dataclass
class Event:
    id: uuid.UUID
    instance_id: uuid.UUID
    event_type: str  # e.g., STATE_CHANGED, WORKER_FAILED, HITL_AWAITING
    payload: Dict[str, Any]
    triggered_by: str  # SYSTEM or USER_ID
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
