import yaml
import uuid
from typing import Set
from flowforge.domain.mission import Mission, MissionState, VALID_STATES, VALID_PRIORITIES

class MissionLoader:
    _global_loaded_ids: Set[uuid.UUID] = set()

    def __init__(self):
        self.instance_loaded_ids: Set[uuid.UUID] = set()

    @classmethod
    def clear_global_ids(cls):
        cls._global_loaded_ids.clear()

    def load(self, yaml_content: str) -> Mission:
        """Parses YAML content, validates schema v1, and tracks duplicate IDs."""
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")

        if not data:
            raise ValueError("Empty or invalid YAML content")

        # 1. Required Fields Validation
        title = data.get("title")
        version = data.get("version")

        if not title:
            raise ValueError("Mission title is required")
        if not version:
            raise ValueError("Mission schema version is required")

        # 2. Schema Version Validation
        if str(version) != "1":
            raise ValueError(f"Unsupported schema version '{version}'. Only version '1' is supported")

        # 3. Status Validation
        status_val = data.get("status", "BACKLOG")
        if status_val not in VALID_STATES:
            raise ValueError(f"Invalid status '{status_val}'. Must be one of {VALID_STATES}")
        status = MissionState(status_val)

        # 4. Priority Validation
        priority = data.get("priority", "medium")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}")

        # 5. UUID / ID Validation & Duplicate Checks
        mission_id_str = data.get("id")
        if mission_id_str:
            try:
                mission_id = uuid.UUID(str(mission_id_str))
            except ValueError:
                raise ValueError("Invalid UUID format for mission id")
        else:
            mission_id = uuid.uuid4()

        # Check duplicates
        if mission_id in self.instance_loaded_ids:
            raise ValueError(f"Duplicate mission ID detected within loader session: {mission_id}")
        if mission_id in self._global_loaded_ids:
            raise ValueError(f"Duplicate mission ID detected globally: {mission_id}")

        self.instance_loaded_ids.add(mission_id)
        self._global_loaded_ids.add(mission_id)

        # Extensible Skema v1 Mapping
        description = data.get("description", "")
        owner = data.get("owner")
        reviewer = data.get("reviewer")
        phase = data.get("phase")
        goal = data.get("goal")
        deliverables = data.get("deliverables", [])
        constraints = data.get("constraints", [])
        definition_of_done = data.get("definition_of_done", [])
        references = data.get("references", [])
        goals = data.get("goals", [])
        metadata = data.get("metadata", {})

        return Mission(
            id=mission_id,
            title=title,
            description=description,
            status=status,
            version=str(version),
            priority=priority,
            owner=owner,
            reviewer=reviewer,
            phase=phase,
            goal=goal,
            deliverables=deliverables,
            constraints=constraints,
            definition_of_done=definition_of_done,
            references=references,
            goals=goals,
            metadata=metadata
        )

    @staticmethod
    def load_from_yaml(yaml_content: str) -> Mission:
        loader = MissionLoader()
        return loader.load(yaml_content)

    @staticmethod
    def load_from_file(file_path: str) -> Mission:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        loader = MissionLoader()
        return loader.load(content)
