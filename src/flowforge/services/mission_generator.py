from typing import Optional, List, Dict, Any
from flowforge.ports.mission_repository import MissionRepository
from flowforge.services.artifact_identity_service import ArtifactIdentityService
from flowforge.domain.mission_factory import MissionFactory
from flowforge.domain.mission import Mission

class MissionGenerator:
    """
    Orchestrates the generation of new missions by determining the next available identifier
    and utilizing the MissionFactory and MissionRepository.
    """
    def __init__(self, repository: MissionRepository):
        self.repository = repository

    async def generate_mission(
        self,
        title: str,
        description: str,
        prefix: str = "PROJECT",
        goals: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: str = "medium"
    ) -> Mission:
        # 1. Get existing identifiers
        existing_identifiers = await self.repository.list_identifiers()
        
        # 2. Determine next identifier
        next_code = ArtifactIdentityService.generate_next_identity(prefix, existing_identifiers)
        
        # 3. Create the Mission object
        mission = MissionFactory.create(
            title=title,
            description=description,
            code=next_code,
            goals=goals,
            metadata=metadata,
            priority=priority
        )
        
        # 4. Save to repository
        await self.repository.save(mission)
        
        return mission
