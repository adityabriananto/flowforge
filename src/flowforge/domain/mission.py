from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

VALID_STATES = {"BACKLOG", "READY", "ACTIVE", "REVIEW", "DONE", "ARCHIVED"}

@dataclass
class Mission:
    id: uuid.UUID
    title: str
    description: str
    status: str  # BACKLOG, READY, ACTIVE, REVIEW, DONE, ARCHIVED
    goals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
