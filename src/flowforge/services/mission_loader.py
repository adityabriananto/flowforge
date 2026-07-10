import yaml
import uuid
from flowforge.domain.mission import Mission, VALID_STATES

class MissionLoader:
    @staticmethod
    def load_from_yaml(yaml_content: str) -> Mission:
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Failed to parse YAML: {str(e)}")

        if not data:
            raise ValueError("Empty or invalid YAML content")

        title = data.get("title")
        description = data.get("description", "")
        status = data.get("status", "BACKLOG")

        if not title:
            raise ValueError("Mission title is required")

        if status not in VALID_STATES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_STATES}")

        mission_id_str = data.get("id")
        if mission_id_str:
            try:
                mission_id = uuid.UUID(str(mission_id_str))
            except ValueError:
                raise ValueError("Invalid UUID format for mission id")
        else:
            mission_id = uuid.uuid4()

        goals = data.get("goals", [])
        metadata = data.get("metadata", {})

        return Mission(
            id=mission_id,
            title=title,
            description=description,
            status=status,
            goals=goals,
            metadata=metadata
        )

    @staticmethod
    def load_from_file(file_path: str) -> Mission:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return MissionLoader.load_from_yaml(content)
