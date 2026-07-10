from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

class SessionStatus(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class SessionMetadata:
    session_id: str
    provider: str
    mission: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    status: SessionStatus = SessionStatus.CREATED

@dataclass
class EngineeringSession:
    metadata: SessionMetadata
    summary: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    open_questions: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    handover_summary: Optional[str] = None
    version: str = "1"
