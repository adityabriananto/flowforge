from abc import ABC, abstractmethod
from typing import Optional, List
from flowforge.domain.agent_profile import AgentProfile

class AgentProfileRepository(ABC):
    @abstractmethod
    async def save(self, profile: AgentProfile) -> None:
        """Saves or updates an Agent Profile in the persistent store."""
        pass

    @abstractmethod
    async def get(self, profile_id: str) -> Optional[AgentProfile]:
        """Retrieves an Agent Profile by its unique ID string."""
        pass

    @abstractmethod
    async def list_all(self) -> List[AgentProfile]:
        """Lists all Agent Profiles present in the persistent store."""
        pass

    @abstractmethod
    async def delete(self, profile_id: str) -> None:
        """Removes an Agent Profile from the persistent store by its ID."""
        pass
