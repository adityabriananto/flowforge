from typing import Optional, List
from flowforge.domain.agent_profile import AgentProfile
from flowforge.ports.agent_profile_repository import AgentProfileRepository

class AgentProfileService:
    def __init__(self, repository: AgentProfileRepository):
        self.repository = repository

    async def save_profile(self, profile: AgentProfile) -> None:
        await self.repository.save(profile)

    async def get_profile(self, profile_id: str) -> Optional[AgentProfile]:
        return await self.repository.get(profile_id)

    async def list_profiles(self) -> List[AgentProfile]:
        return await self.repository.list_all()

    async def delete_profile(self, profile_id: str) -> None:
        await self.repository.delete(profile_id)

    async def find_profiles_by_capability(self, capability_name: str, min_score: int = 50) -> List[AgentProfile]:
        """Filters agent profiles that support a specific capability with a score >= min_score."""
        profiles = await self.repository.list_all()
        matching_profiles = []
        for profile in profiles:
            score = profile.capabilities.get(capability_name, 0)
            if score >= min_score:
                matching_profiles.append(profile)
        # Sort by capability score descending
        matching_profiles.sort(key=lambda p: p.capabilities[capability_name], reverse=True)
        return matching_profiles
