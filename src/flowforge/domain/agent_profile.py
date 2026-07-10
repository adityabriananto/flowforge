from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

VALID_EXECUTION_MODES = {"api", "cli", "agentic", "interactive", "batch"}

@dataclass
class AgentProfile:
    id: str
    display_name: str
    version: str
    provider: str
    capabilities: Dict[str, int]  # capability name -> score/rating (0-100)
    limitations: List[str] = field(default_factory=list)
    preferred_output: str = "text"
    context_limit: int = 4096
    supported_languages: List[str] = field(default_factory=list)
    supported_frameworks: List[str] = field(default_factory=list)
    execution_mode: str = "api"  # api, cli, agentic, interactive, batch
    metadata: Dict[str, Any] = field(default_factory=dict)
