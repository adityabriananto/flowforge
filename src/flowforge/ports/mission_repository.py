from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from flowforge.domain.mission import Mission

class MissionRepository(ABC):
    @abstractmethod
    async def save(self, mission: Mission) -> None:
        """Saves or updates a mission in the persistent store."""
        pass

    @abstractmethod
    async def get(self, mission_id: uuid.UUID) -> Optional[Mission]:
        """Retrieves a mission by its unique UUID identifier."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Mission]:
        """Lists all missions present in the persistent store."""
        pass

    @abstractmethod
    async def delete(self, mission_id: uuid.UUID) -> None:
        """Removes a mission from the persistent store by its ID."""
        pass
