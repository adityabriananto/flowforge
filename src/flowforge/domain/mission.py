from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from enum import Enum

class MissionState(str, Enum):
    BACKLOG = "BACKLOG"
    READY = "READY"
    ACTIVE = "ACTIVE"
    REVIEW = "REVIEW"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"

VALID_STATES = {state.value for state in MissionState}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}

@dataclass
class Mission:
    id: uuid.UUID
    title: str
    description: str
    status: MissionState
    code: Optional[str] = None
    version: str = "1"
    priority: str = "medium"
    owner: Optional[str] = None
    reviewer: Optional[str] = None
    phase: Optional[str] = None
    goal: Optional[str] = None
    deliverables: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    definition_of_done: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)  # Keep backward compatibility
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
