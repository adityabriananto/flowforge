import os
import yaml
import uuid
from typing import Dict, Any, List, Optional
from flowforge.services.workspace.engineering_workspace import EngineeringWorkspace
from flowforge.services.mission_loader import MissionLoader

class MissionLifecycleManager:
    """
    Manages the lifecycle of Mission YAML files inside the Engineering Workspace
    and synchronizes PROJECT_STATE.yaml.
    """
    
    @staticmethod
    def _get_project_state_path(base_path: str) -> str:
        return os.path.join(base_path, "engineering", "PROJECT_STATE.yaml")

    @classmethod
    def get_project_state(cls, base_path: str = ".") -> Dict[str, Any]:
        path = cls._get_project_state_path(base_path)
        if not os.path.exists(path):
            return {
                "active_missions": [],
                "completed_missions": []
            }
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {"active_missions": [], "completed_missions": []}
        except Exception:
            return {"active_missions": [], "completed_missions": []}

    @classmethod
    def write_project_state(cls, state: Dict[str, Any], base_path: str = ".") -> None:
        path = cls._get_project_state_path(base_path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(state, f, sort_keys=False, default_flow_style=False)

    @classmethod
    def _find_mission_file(cls, mission_id: str, base_path: str = ".") -> tuple[Optional[str], Optional[str]]:
        """Returns tuple of (folder_name, file_path) if found, otherwise (None, None)."""
        states = ["backlog", "active", "completed"]
        for state in states:
            folder = os.path.join(base_path, "engineering", "missions", state)
            if not os.path.exists(folder):
                continue
            for file_name in os.listdir(folder):
                if file_name.endswith(".yaml"):
                    file_path = os.path.join(folder, file_name)
                    try:
                        # Load file to verify ID
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                        if data and str(data.get("id")) == str(mission_id):
                            return state, file_path
                    except Exception:
                        pass
        return None, None

    @classmethod
    def create_mission(
        cls, 
        title: str, 
        description: str, 
        mission_id: Optional[str] = None, 
        base_path: str = "."
    ) -> str:
        """Creates a new mission in backlog using the template."""
        # Ensure workspace folders exist
        EngineeringWorkspace.initialize_workspace(base_path)
        
        m_id = mission_id or str(uuid.uuid4())
        
        # Verify duplicate ID
        state_found, _ = cls._find_mission_file(m_id, base_path)
        if state_found:
            raise ValueError(f"Duplicate Mission ID: A mission with ID '{m_id}' already exists.")

        template_path = os.path.join(base_path, "engineering", "missions", "templates", "mission.yaml")
        if not os.path.exists(template_path):
            raise FileNotFoundError("Mission template file not found. Run initialize_workspace first.")

        with open(template_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)

        # Update metadata
        template_data["id"] = m_id
        template_data["title"] = title
        template_data["description"] = description
        template_data["status"] = "BACKLOG"

        dest_file = os.path.join(base_path, "engineering", "missions", "backlog", f"{m_id}.yaml")
        with open(dest_file, "w", encoding="utf-8") as f:
            yaml.dump(template_data, f, sort_keys=False, default_flow_style=False)
            
        return dest_file

    @classmethod
    def list_missions(cls, base_path: str = ".") -> Dict[str, List[Dict[str, Any]]]:
        """Lists all missions in the engineering workspace grouped by state."""
        EngineeringWorkspace.initialize_workspace(base_path)
        grouped = {"backlog": [], "active": [], "completed": []}
        
        for state in grouped.keys():
            folder = os.path.join(base_path, "engineering", "missions", state)
            if not os.path.exists(folder):
                continue
            for file_name in os.listdir(folder):
                if file_name.endswith(".yaml"):
                    file_path = os.path.join(folder, file_name)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                        if data:
                            grouped[state].append({
                                "id": data.get("id"),
                                "title": data.get("title"),
                                "status": data.get("status"),
                                "file_name": file_name
                            })
                    except Exception:
                        pass
        return grouped

    @classmethod
    def show_mission(cls, mission_id: str, base_path: str = ".") -> Dict[str, Any]:
        """Loads and returns mission data."""
        state, file_path = cls._find_mission_file(mission_id, base_path)
        if not file_path:
            raise FileNotFoundError(f"Mission '{mission_id}' not found.")
            
        # Standard load and validate using existing MissionLoader
        return MissionLoader.load_from_file(file_path)

    @classmethod
    def start_mission(cls, mission_id: str, base_path: str = ".") -> str:
        """Transitions mission from backlog to active."""
        state, file_path = cls._find_mission_file(mission_id, base_path)
        if not file_path:
            raise FileNotFoundError(f"Mission '{mission_id}' not found.")

        if state != "backlog":
            raise ValueError(f"Invalid transition. Mission '{mission_id}' is in '{state}' state, cannot start.")

        # Read, update status inside file, then write back
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data["status"] = "ACTIVE"
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

        # Move file physically
        filename = os.path.basename(file_path)
        new_path = EngineeringWorkspace.move_mission_file(filename, "backlog", "active", base_path)

        # Sync PROJECT_STATE.yaml
        project_state = cls.get_project_state(base_path)
        if mission_id not in project_state["active_missions"]:
            project_state["active_missions"].append(mission_id)
        if mission_id in project_state.get("completed_missions", []):
            project_state["completed_missions"].remove(mission_id)
        cls.write_project_state(project_state, base_path)

        return new_path

    @classmethod
    def complete_mission(cls, mission_id: str, base_path: str = ".") -> str:
        """Transitions mission from active to completed."""
        state, file_path = cls._find_mission_file(mission_id, base_path)
        if not file_path:
            raise FileNotFoundError(f"Mission '{mission_id}' not found.")

        if state != "active":
            raise ValueError(f"Invalid transition. Mission '{mission_id}' is in '{state}' state, cannot complete.")

        # Read, update status inside file, then write back
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data["status"] = "DONE"
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

        # Move file physically
        filename = os.path.basename(file_path)
        new_path = EngineeringWorkspace.move_mission_file(filename, "active", "completed", base_path)

        # Sync PROJECT_STATE.yaml
        project_state = cls.get_project_state(base_path)
        if mission_id in project_state["active_missions"]:
            project_state["active_missions"].remove(mission_id)
        if "completed_missions" not in project_state:
            project_state["completed_missions"] = []
        if mission_id not in project_state["completed_missions"]:
            project_state["completed_missions"].append(mission_id)
        cls.write_project_state(project_state, base_path)

        return new_path
