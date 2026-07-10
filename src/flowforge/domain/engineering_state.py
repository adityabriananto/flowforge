from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class ProjectState:
    id: str
    name: str

@dataclass
class WorkspaceState:
    version: str = "1"
    engineering_phase: str = "init"

@dataclass
class MissionState:
    current_mission: Optional[str] = None
    completed_missions: List[str] = field(default_factory=list)
    mission_history: List[str] = field(default_factory=list)

@dataclass
class ProviderUsage:
    provider: str
    mission: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

@dataclass
class ProviderState:
    current_provider: Optional[str] = None
    provider_history: List[ProviderUsage] = field(default_factory=list)

@dataclass
class SessionState:
    current_session_id: Optional[str] = None
    latest_session_id: Optional[str] = None

@dataclass
class KnowledgeEntry:
    id: str
    title: str
    reference_path: str
    category: str  # e.g., repository, architecture, technical_debt, security, performance, backend, frontend, api, infrastructure
    extracted_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KnowledgeState:
    knowledge: List[KnowledgeEntry] = field(default_factory=list)

@dataclass
class DecisionEntry:
    id: str
    title: str
    rationale: str
    mission: Optional[str] = None
    artifact_reference: Optional[str] = None
    decided_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DecisionState:
    decisions: List[DecisionEntry] = field(default_factory=list)

@dataclass
class EngineeringEvent:
    id: str
    event_type: str  # e.g., Mission Started, Mission Completed, Provider Changed, Decision Approved, Artifact Generated, Engineering State Updated
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TimelineState:
    event_log: List[EngineeringEvent] = field(default_factory=list)

@dataclass
class OpenQuestion:
    id: str
    title: str
    description: str
    mission: Optional[str] = None
    status: str = "open"  # e.g., open, resolved
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

@dataclass
class BlockerEntry:
    id: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RecommendationEntry:
    id: str
    suggestion: str
    proposed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EngineeringState:
    project: ProjectState
    workspace: WorkspaceState = field(default_factory=WorkspaceState)
    mission: MissionState = field(default_factory=MissionState)
    provider: ProviderState = field(default_factory=ProviderState)
    session: SessionState = field(default_factory=SessionState)
    knowledge_state: KnowledgeState = field(default_factory=KnowledgeState)
    decision_state: DecisionState = field(default_factory=DecisionState)
    timeline_state: TimelineState = field(default_factory=TimelineState)
    open_questions: List[OpenQuestion] = field(default_factory=list)
    blockers: List[BlockerEntry] = field(default_factory=list)
    recommendations: List[RecommendationEntry] = field(default_factory=list)
    version: str = "1"
