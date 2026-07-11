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
    def _find_mission_file(cls, mission_id_or_code: str, base_path: str = ".") -> tuple[Optional[str], Optional[str]]:
        """Returns tuple of (folder_name, file_path) if found, otherwise (None, None). Matches ID, Code, or Filename."""
        states = ["backlog", "active", "completed"]
        for state in states:
            folder = os.path.join(base_path, "engineering", "missions", state)
            if not os.path.exists(folder):
                continue
            for file_name in os.listdir(folder):
                if file_name.endswith(".yaml"):
                    file_path = os.path.join(folder, file_name)
                    name_without_ext = os.path.splitext(file_name)[0]
                    
                    # Direct filename match (e.g. PROJECT-000.yaml)
                    if name_without_ext.lower() == str(mission_id_or_code).lower():
                        return state, file_path
                        
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                        if data:
                            yaml_id = str(data.get("id", ""))
                            yaml_code = str(data.get("code", ""))
                            if yaml_id.lower() == str(mission_id_or_code).lower() or yaml_code.lower() == str(mission_id_or_code).lower():
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
        base_path: str = ".",
        goal: Optional[str] = None,
        deliverables: Optional[List[str]] = None,
        definition_of_done: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ) -> str:
        """Creates a new mission in backlog using the template with UUID id and custom code."""
        # Ensure workspace folders exist
        EngineeringWorkspace.initialize_workspace(base_path)
        
        # Determine if input mission_id is a valid UUID
        m_id_is_uuid = False
        if mission_id:
            try:
                uuid.UUID(str(mission_id))
                m_id_is_uuid = True
            except ValueError:
                pass

        if m_id_is_uuid:
            m_uuid = str(mission_id)
            m_code = str(mission_id)
        else:
            m_uuid = str(uuid.uuid4())
            # Gather all existing identifiers across all lifecycle states
            existing_identifiers = []
            grouped_missions = cls.list_missions(base_path)
            for group in grouped_missions.values():
                for m_data in group:
                    if m_data.get("code"):
                        existing_identifiers.append(m_data["code"])
                        
            from flowforge.services.artifact_identity_service import ArtifactIdentityService
            prefix = "PROJECT" # Default engineering prefix for missions
            m_code = mission_id or ArtifactIdentityService.generate_next_identity(prefix, existing_identifiers)
        
        # Verify duplicate ID/Code
        state_found, _ = cls._find_mission_file(m_code, base_path)
        if state_found:
            raise ValueError(f"Duplicate Mission ID/Code: A mission with ID or Code '{m_code}' already exists.")

        template_path = os.path.join(base_path, "engineering", "missions", "templates", "mission.yaml")
        if not os.path.exists(template_path):
            raise FileNotFoundError("Mission template file not found. Run initialize_workspace first.")

        with open(template_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)

        # Update metadata
        template_data["id"] = m_uuid
        template_data["code"] = m_code
        template_data["title"] = title
        template_data["description"] = description
        template_data["status"] = "BACKLOG"
        
        if goal:
            template_data["goal"] = goal
        if deliverables is not None:
            template_data["deliverables"] = deliverables
        if definition_of_done is not None:
            template_data["definition_of_done"] = definition_of_done
        if constraints is not None:
            template_data["constraints"] = constraints

        dest_file = os.path.join(base_path, "engineering", "missions", "backlog", f"{m_code}.yaml")
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
        resolved_code = data.get("code") or os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

        # Move file physically
        filename = os.path.basename(file_path)
        new_path = EngineeringWorkspace.move_mission_file(filename, "backlog", "active", base_path)

        # Sync PROJECT_STATE.yaml
        project_state = cls.get_project_state(base_path)
        if resolved_code not in project_state["active_missions"]:
            project_state["active_missions"].append(resolved_code)
        if resolved_code in project_state.get("completed_missions", []):
            project_state["completed_missions"].remove(resolved_code)
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
        resolved_code = data.get("code") or os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

        # Move file physically
        filename = os.path.basename(file_path)
        new_path = EngineeringWorkspace.move_mission_file(filename, "active", "completed", base_path)

        # Sync PROJECT_STATE.yaml
        project_state = cls.get_project_state(base_path)
        if resolved_code in project_state["active_missions"]:
            project_state["active_missions"].remove(resolved_code)
        if "completed_missions" not in project_state:
            project_state["completed_missions"] = []
        if resolved_code not in project_state["completed_missions"]:
            project_state["completed_missions"].append(resolved_code)
        cls.write_project_state(project_state, base_path)

        return new_path
