import yaml
from typing import Set, Dict, Any
from flowforge.domain.agent_profile import AgentProfile, VALID_EXECUTION_MODES

class AgentProfileLoader:
    _global_loaded_ids: Set[str] = set()

    def __init__(self):
        self.instance_loaded_ids: Set[str] = set()

    @classmethod
    def clear_global_ids(cls):
        cls._global_loaded_ids.clear()

    def load(self, yaml_content: str) -> AgentProfile:
        """Parses YAML content, validates constraints, and returns an AgentProfile instance."""
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")

        if not data:
            raise ValueError("Empty or invalid YAML content")

        # 1. Required Fields Validation
        required_keys = ["id", "display_name", "version", "provider", "capabilities", "execution_mode"]
        for key in required_keys:
            if key not in data or data[key] is None:
                raise ValueError(f"Required field '{key}' is missing")

        profile_id = str(data["id"]).strip()
        display_name = str(data["display_name"]).strip()
        version = str(data["version"]).strip()
        provider = str(data["provider"]).strip()
        capabilities = data["capabilities"]
        execution_mode = str(data["execution_mode"]).strip().lower()

        if not profile_id:
            raise ValueError("Required field 'id' cannot be empty")
        if not display_name:
            raise ValueError("Required field 'display_name' cannot be empty")
        if not version:
            raise ValueError("Required field 'version' cannot be empty")
        if not provider:
            raise ValueError("Required field 'provider' cannot be empty")

        # 2. Schema Version Validation
        if version != "1":
            raise ValueError(f"Unsupported schema version '{version}'. Only version '1' is supported")

        # 3. Duplicate ID Check
        id_key = profile_id.lower()
        if id_key in self.instance_loaded_ids:
            raise ValueError(f"Duplicate agent profile ID detected within loader session: {profile_id}")
        if id_key in self._global_loaded_ids:
            raise ValueError(f"Duplicate agent profile ID detected globally: {profile_id}")

        self.instance_loaded_ids.add(id_key)
        self._global_loaded_ids.add(id_key)

        # 4. Capability Definitions Validation
        if not isinstance(capabilities, dict):
            raise ValueError("Field 'capabilities' must be a dictionary")

        validated_capabilities: Dict[str, int] = {}
        for cap_name, score in capabilities.items():
            try:
                score_int = int(score)
            except (ValueError, TypeError):
                raise ValueError(f"Capability score for '{cap_name}' must be an integer")
            
            if score_int < 0 or score_int > 100:
                raise ValueError(f"Capability score for '{cap_name}' must be between 0 and 100")
            
            validated_capabilities[str(cap_name)] = score_int

        # 5. Execution Mode Validation
        if execution_mode not in VALID_EXECUTION_MODES:
            raise ValueError(f"Invalid execution mode '{execution_mode}'. Must be one of {VALID_EXECUTION_MODES}")

        # Extensible Fields
        limitations = data.get("limitations", [])
        preferred_output = data.get("preferred_output", "text")
        context_limit = data.get("context_limit", 4096)
        supported_languages = data.get("supported_languages", [])
        supported_frameworks = data.get("supported_frameworks", [])
        metadata = data.get("metadata", {})

        return AgentProfile(
            id=profile_id,
            display_name=display_name,
            version=version,
            provider=provider,
            capabilities=validated_capabilities,
            limitations=limitations,
            preferred_output=preferred_output,
            context_limit=int(context_limit),
            supported_languages=supported_languages,
            supported_frameworks=supported_frameworks,
            execution_mode=execution_mode,
            metadata=metadata
        )

    def load_from_file(self, file_path: str) -> AgentProfile:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.load(content)

    @staticmethod
    def load_from_yaml(yaml_content: str) -> AgentProfile:
        loader = AgentProfileLoader()
        return loader.load(yaml_content)

    @staticmethod
    def load_from_file(file_path: str) -> AgentProfile:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        loader = AgentProfileLoader()
        return loader.load(content)
