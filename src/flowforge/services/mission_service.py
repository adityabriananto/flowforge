import uuid
from datetime import datetime, timezone
from typing import Optional, List
from flowforge.domain.mission import Mission, VALID_STATES
from flowforge.ports.mission_repository import MissionRepository

class MissionService:
    def __init__(self, repository: MissionRepository):
        self.repository = repository

    async def create_mission(
        self, 
        title: str, 
        description: str, 
        goals: Optional[List[str]] = None, 
        metadata: Optional[dict] = None
    ) -> Mission:
        mission = Mission(
            id=uuid.uuid4(),
            title=title,
            description=description,
            status="BACKLOG",
            goals=goals or [],
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await self.repository.save(mission)
        return mission

    async def get_mission(self, mission_id: uuid.UUID) -> Optional[Mission]:
        return await self.repository.get(mission_id)

    async def update_status(self, mission_id: uuid.UUID, new_status: str) -> Mission:
        if new_status not in VALID_STATES:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of {VALID_STATES}")
        
        mission = await self.repository.get(mission_id)
        if not mission:
            raise ValueError(f"Mission with ID {mission_id} not found")
        
        mission.status = new_status
        mission.updated_at = datetime.now(timezone.utc)
        
        await self.repository.save(mission)
        return mission

    async def list_missions(self) -> List[Mission]:
        return await self.repository.list_all()

    async def delete_mission(self, mission_id: uuid.UUID) -> None:
        await self.repository.delete(mission_id)
