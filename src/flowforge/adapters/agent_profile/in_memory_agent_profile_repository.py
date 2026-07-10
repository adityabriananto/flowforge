from typing import Optional, List, Dict
from flowforge.ports.agent_profile_repository import AgentProfileRepository
from flowforge.domain.agent_profile import AgentProfile

class InMemoryAgentProfileRepository(AgentProfileRepository):
    def __init__(self):
        self._profiles: Dict[str, AgentProfile] = {}

    async def save(self, profile: AgentProfile) -> None:
        self._profiles[profile.id.lower()] = profile

    async def get(self, profile_id: str) -> Optional[AgentProfile]:
        return self._profiles.get(profile_id.lower())

    async def list_all(self) -> List[AgentProfile]:
        return list(self._profiles.values())

    async def delete(self, profile_id: str) -> None:
        key = profile_id.lower()
        if key in self._profiles:
            del self._profiles[key]
