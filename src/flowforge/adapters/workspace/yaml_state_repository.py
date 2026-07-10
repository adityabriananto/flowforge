import os
import yaml
from flowforge.ports.state_repository import EngineeringStateRepository
from flowforge.domain.engineering_state import EngineeringState
from flowforge.services.workspace.state_loader import EngineeringStateLoader

class YAMLEngineeringStateRepository(EngineeringStateRepository):
    def __init__(self, filename: str = "ENGINEERING_STATE.yaml"):
        self.filename = filename

    def _get_path(self, base_path: str) -> str:
        return os.path.join(base_path, "engineering", self.filename)

    def load(self, base_path: str = ".") -> EngineeringState:
        path = self._get_path(base_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"ENGINEERING_STATE.yaml not found at: {path}")
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return EngineeringStateLoader.load_from_yaml(content)

    def save(self, state: EngineeringState, base_path: str = ".") -> None:
        path = self._get_path(base_path)
        
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        state_dict = EngineeringStateLoader.to_dict(state)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(state_dict, f, sort_keys=False, default_flow_style=False)
