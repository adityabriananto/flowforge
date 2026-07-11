from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class MissionPackage:
    mission_summary: str
    objective: str
    deliverables: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    relevant_rules: List[str] = field(default_factory=list)
    relevant_context: Dict[str, Any] = field(default_factory=dict)
    relevant_references: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    definition_of_done: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
