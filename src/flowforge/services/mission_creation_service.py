from typing import Optional, List, Dict, Any
from flowforge.ports.mission_repository import MissionRepository
from flowforge.services.artifact_identity_service import ArtifactIdentityService
from flowforge.domain.mission import Mission
from flowforge.services.planning_context_builder import PlanningContextBuilder
from flowforge.services.mission_planning_engine import MissionPlanningEngine
from flowforge.services.mission_review_service import MissionReviewService

class MissionCreationService:
    """
    Orchestrates the new Mission Authoring workflow:
    Identity -> Context -> Planning -> Review -> Repository.save
    """
    def __init__(
        self, 
        repository: MissionRepository, 
        base_path: str = ".",
        review_service: Optional[MissionReviewService] = None
    ):
        self.repository = repository
        self.base_path = base_path
        self.context_builder = PlanningContextBuilder(base_path)
        self.planning_engine = MissionPlanningEngine()
        self.review_service = review_service or MissionReviewService()

    async def create_mission(
        self,
        title: str,
        goal: str,
        priority: str = "medium",
        prefix: str = "PROJECT",
        notes: Optional[str] = None
    ) -> Optional[Mission]:
        """
        Creates and saves a mission after planning and developer review.
        Returns the Mission if accepted, None if rejected.
        """
        # 1. Identity
        existing_identifiers = await self.repository.list_identifiers()
        next_code = ArtifactIdentityService.generate_next_identity(prefix, existing_identifiers)
        
        # 2. Context
        context = self.context_builder.build_context()
        
        # 3. Planning
        mission = self.planning_engine.generate_draft(
            context=context,
            title=title,
            goal=goal,
            priority=priority,
            code=next_code,
            notes=notes
        )
        
        # 4. Review
        accepted = self.review_service.review_mission(mission)
        
        # 5. Persistence
        if accepted:
            await self.repository.save(mission)
            return mission
        
        return None
