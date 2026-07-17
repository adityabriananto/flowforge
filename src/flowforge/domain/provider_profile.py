from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ProviderConfig:
    name: str
    provider: str
    type: str  # 'api' or 'cli'
    model: Optional[str] = None
    api_key_env: Optional[str] = None
    endpoint: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = field(default_factory=list)

@dataclass
class ProfileConfig:
    name: str
    provider: str
    temperature: float = 0.0
    max_tokens: int = 4096
