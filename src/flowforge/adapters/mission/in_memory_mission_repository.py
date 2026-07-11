from typing import Optional, List, Dict
import uuid
from flowforge.ports.mission_repository import MissionRepository
from flowforge.domain.mission import Mission

class InMemoryMissionRepository(MissionRepository):
    def __init__(self):
        self._missions: Dict[uuid.UUID, Mission] = {}

    async def save(self, mission: Mission) -> None:
        self._missions[mission.id] = mission

    async def get(self, mission_id: uuid.UUID) -> Optional[Mission]:
        return self._missions.get(mission_id)

    async def list_all(self) -> List[Mission]:
        return list(self._missions.values())

    async def delete(self, mission_id: uuid.UUID) -> None:
        if mission_id in self._missions:
            del self._missions[mission_id]

    async def list_identifiers(self) -> List[str]:
        return [m.code for m in self._missions.values() if m.code]
