import os
import uuid
import yaml
from typing import Optional, List
from flowforge.domain.mission import Mission, MissionState
from flowforge.ports.mission_repository import MissionRepository
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

class YamlMissionRepository(MissionRepository):
    """
    A file-system based repository for Missions, leveraging the Engineering Workspace layout.
    """
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    async def save(self, mission: Mission) -> None:
        """
        Saves the mission to the appropriate YAML file in the workspace.
        """
        # For new missions, we save to backlog if status is BACKLOG
        # (This is a simplified save for generation)
        
        # Hydrate template or create dict
        template_data = {
            "id": str(mission.id),
            "code": mission.code,
            "title": mission.title,
            "description": mission.description,
            "status": mission.status.value,
            "version": mission.version,
            "priority": mission.priority,
            "deliverables": mission.deliverables,
            "definition_of_done": mission.definition_of_done,
            "constraints": mission.constraints,
            "goals": mission.goals,
            "metadata": mission.metadata
        }
        
        # Determine folder based on status
        folder = "backlog"
        if mission.status == MissionState.ACTIVE:
            folder = "active"
        elif mission.status == MissionState.DONE or mission.status.value == "COMPLETED":
            folder = "completed"
            
        dest_dir = os.path.join(self.base_path, "engineering", "missions", folder)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Use code if available, else id
        filename = f"{mission.code or mission.id}.yaml"
        dest_file = os.path.join(dest_dir, filename)
        
        with open(dest_file, "w", encoding="utf-8") as f:
            yaml.dump(template_data, f, sort_keys=False, default_flow_style=False)

    async def get(self, mission_id: uuid.UUID) -> Optional[Mission]:
        # Not strictly required for the generation flow right now, but part of the port
        pass

    async def list_all(self) -> List[Mission]:
        pass

    async def delete(self, mission_id: uuid.UUID) -> None:
        pass

    async def list_identifiers(self) -> List[str]:
        """
        Lists all existing mission identifiers (codes) across all folders.
        """
        identifiers = []
        try:
            grouped = MissionLifecycleManager.list_missions(self.base_path)
            for group in grouped.values():
                for m_data in group:
                    if m_data.get("code"):
                        identifiers.append(m_data["code"])
        except Exception:
            pass # Workspace might not exist yet
        return identifiers
