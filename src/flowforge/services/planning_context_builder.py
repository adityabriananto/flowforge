import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from flowforge.services.workspace.state_service import EngineeringStateService
from flowforge.adapters.workspace.yaml_state_repository import YAMLEngineeringStateRepository
from flowforge.services.workspace.mission_lifecycle_manager import MissionLifecycleManager

@dataclass
class PlanningContext:
    framework: str = "unknown"
    language: str = "unknown"
    project_type: str = "unknown"
    existing_missions: int = 0
    recent_adrs: List[str] = field(default_factory=list)
    recent_rfcs: List[str] = field(default_factory=list)

class PlanningContextBuilder:
    """
    Collects Engineering Workspace knowledge to normalize engineering metadata.
    Does not scan repository source code, relies entirely on structured workspace data.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.state_service = EngineeringStateService(YAMLEngineeringStateRepository())

    def build_context(self) -> PlanningContext:
        context = PlanningContext()
        
        # Extract from PROJECT_STATE if available
        try:
            state = self.state_service.load_state(self.base_path)
            context.framework = state.context.get("framework", "unknown")
            context.language = state.context.get("language", "unknown")
            context.project_type = state.context.get("project_type", "unknown")
        except Exception:
            pass # State might not exist or be invalid yet
            
        # Count existing missions
        try:
            grouped = MissionLifecycleManager.list_missions(self.base_path)
            context.existing_missions = sum(len(m_list) for m_list in grouped.values())
        except Exception:
            pass
            
        # Find ADRs/RFCs (just the filenames as a hint)
        context.recent_adrs = self._list_templates("adr")
        context.recent_rfcs = self._list_templates("rfc")
        
        return context
        
    def _list_templates(self, doc_type: str) -> List[str]:
        # For simplicity, we just look at the templates folder or docs folder.
        # FlowForge keeps ADRs/RFCs typically inside docs/ or engineering/docs/
        # Currently, they might just be listed in templates or we can scan engineering/docs
        docs_path = os.path.join(self.base_path, "engineering", "docs", doc_type)
        if not os.path.exists(docs_path):
            return []
            
        docs = []
        try:
            for file_name in os.listdir(docs_path):
                if file_name.endswith(".md"):
                    docs.append(file_name.replace(".md", ""))
        except Exception:
            pass
        return docs
