from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExecutionResult:
    status: str  # "SUCCESS" or "FAILED"
    summary: str
    artifacts: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    open_questions: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    handover_summary: Optional[str] = None
    duration_seconds: float = 0.0
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
