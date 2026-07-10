import os
import yaml
from flowforge.ports.session_repository import EngineeringSessionRepository
from flowforge.domain.engineering_session import EngineeringSession
from flowforge.services.workspace.session_loader import EngineeringSessionLoader

class YAMLEngineeringSessionRepository(EngineeringSessionRepository):
    def _get_path(self, session_id: str, base_path: str) -> str:
        return os.path.join(base_path, ".flowforge", "logs", f"session_{session_id}.yaml")

    def load(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        path = self._get_path(session_id, base_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"EngineeringSession file not found at: {path}")
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return EngineeringSessionLoader.load_from_yaml(content)

    def save(self, session: EngineeringSession, base_path: str = ".") -> None:
        path = self._get_path(session.metadata.session_id, base_path)
        
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        session_dict = EngineeringSessionLoader.to_dict(session)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(session_dict, f, sort_keys=False, default_flow_style=False)
