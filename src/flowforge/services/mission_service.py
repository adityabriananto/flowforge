import uuid
from datetime import datetime, timezone
from typing import Optional, List, Union
from flowforge.domain.mission import Mission, MissionState, VALID_STATES
from flowforge.ports.mission_repository import MissionRepository

class MissionService:
    def __init__(self, repository: MissionRepository):
        self.repository = repository

    async def create_mission(
        self, 
        title: str, 
        description: str, 
        goals: Optional[List[str]] = None, 
        metadata: Optional[dict] = None,
        priority: str = "medium"
    ) -> Mission:
        mission = Mission(
            id=uuid.uuid4(),
            title=title,
            description=description,
            status=MissionState.BACKLOG,
            goals=goals or [],
            metadata=metadata or {},
            priority=priority,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await self.repository.save(mission)
        return mission

    async def get_mission(self, mission_id: uuid.UUID) -> Optional[Mission]:
        return await self.repository.get(mission_id)

    async def update_status(self, mission_id: uuid.UUID, new_status: Union[str, MissionState]) -> Mission:
        # Convert string to Enum if needed
        status_str = new_status.value if isinstance(new_status, MissionState) else new_status
        
        if status_str not in VALID_STATES:
            raise ValueError(f"Invalid status '{status_str}'. Must be one of {VALID_STATES}")
        
        mission = await self.repository.get(mission_id)
        if not mission:
            raise ValueError(f"Mission with ID {mission_id} not found")
        
        mission.status = MissionState(status_str)
        mission.updated_at = datetime.now(timezone.utc)
        
        await self.repository.save(mission)
        return mission

    async def list_missions(self) -> List[Mission]:
        return await self.repository.list_all()

    async def delete_mission(self, mission_id: uuid.UUID) -> None:
        await self.repository.delete(mission_id)
