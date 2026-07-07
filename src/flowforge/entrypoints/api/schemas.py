from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

class StateConfigSchema(BaseModel):
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

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    initial_state: str = Field(..., min_length=1)
    states: Dict[str, StateConfigSchema]

class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    version: str
    initial_state: str
    states: Dict[str, StateConfigSchema]
    created_at: datetime

class InstanceCreate(BaseModel):
    workflow_id: uuid.UUID
    variables: Dict[str, Any] = Field(default_factory=dict)

class InstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    current_state: str
    variables: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class TransitionRequest(BaseModel):
    event: str = Field(..., min_length=1)
    triggered_by: str = "SYSTEM"

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    instance_id: uuid.UUID
    event_type: str
    payload: Dict[str, Any]
    triggered_by: str
    timestamp: datetime
