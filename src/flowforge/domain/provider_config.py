from dataclasses import dataclass, field
from typing import List

@dataclass
class CliProviderConfig:
    executable: str
    command: str
    args: List[str] = field(default_factory=list)
