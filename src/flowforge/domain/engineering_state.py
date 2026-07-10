from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class ProjectState:
    id: str
    name: str

@dataclass
class WorkspaceState:
    version: str = "1"
    engineering_phase: str = "init"

@dataclass
class MissionStateInfo:
    current_mission: Optional[str] = None
    completed_missions: List[str] = field(default_factory=list)
    mission_history: List[str] = field(default_factory=list)

@dataclass
class ProviderStateInfo:
    current_provider: Optional[str] = None
    provider_history: List[str] = field(default_factory=list)

@dataclass
class SessionStateInfo:
    current_session_id: Optional[str] = None
    latest_session_id: Optional[str] = None

@dataclass
class KnowledgeEntry:
    id: str
    title: str
    reference_path: str
    extracted_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DecisionEntry:
    id: str
    title: str
    rationale: str
    decided_at: datetime = field(default_factory=datetime.utcnow)

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
class MilestoneEntry:
    id: str
    title: str
    target_date: Optional[str] = None

@dataclass
class EngineeringState:
    project: ProjectState
    workspace: WorkspaceState = field(default_factory=WorkspaceState)
    mission: MissionStateInfo = field(default_factory=MissionStateInfo)
    provider: ProviderStateInfo = field(default_factory=ProviderStateInfo)
    session: SessionStateInfo = field(default_factory=SessionStateInfo)
    knowledge: List[KnowledgeEntry] = field(default_factory=list)
    decisions: List[DecisionEntry] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    blockers: List[BlockerEntry] = field(default_factory=list)
    recommendations: List[RecommendationEntry] = field(default_factory=list)
    timeline: List[MilestoneEntry] = field(default_factory=list)
    version: str = "1"
