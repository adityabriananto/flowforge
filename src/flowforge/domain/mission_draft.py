from dataclasses import dataclass
from enum import Enum
from flowforge.domain.mission import Mission
from flowforge.services.planning_context_builder import PlanningContext

@dataclass(frozen=True)
class DeveloperInput:
    title: str
    business_goal: str
    priority: str

class MissionReviewAction(str, Enum):
    ACCEPT = "ACCEPT"
    EDIT = "EDIT"
    CANCEL = "CANCEL"

@dataclass(frozen=True)
class MissionDraft:
    developer_input: DeveloperInput
    planning_context: PlanningContext
    generated_mission: Mission
