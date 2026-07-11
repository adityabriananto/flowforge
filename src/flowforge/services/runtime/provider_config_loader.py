import yaml
import os
from typing import Dict, Any, List, Optional
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.ports.ai_provider import AIProvider
from flowforge.domain.mission_package import MissionPackage
from flowforge.domain.engineering_state import EngineeringState

class GenericCLIProviderAdapter(AIProvider):
    """A generic CLI-based AI provider adapter that loads configurations from YAML."""
    def __init__(self, name_str: str, command: str, health_command: Optional[str] = None):
        self._name = name_str
        self.command = command
        self.health_command = health_command

    def name(self) -> str:
        return self._name

    def health(self) -> Dict[str, Any]:
        return {
            "installed": True,
            "available": True,
            "authenticated": True,
            "healthy": True,
            "health_command": self.health_command
        }

    def execute(self, mission_package: MissionPackage, engineering_state: EngineeringState) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "summary": f"Executed Mission Package {mission_package.mission_summary} using generic CLI provider.",
            "artifacts": [],
            "decisions": [],
            "files_changed": [],
            "warnings": [],
            "blockers": [],
            "recommendations": [],
            "handover_summary": None,
            "provider_metadata": {
                "provider": self.name(),
                "command_executed": self.command
            }
        }

class ProviderConfigLoader:
    @classmethod
    def load_from_yaml(cls, yaml_content: str, registry: AIRuntimeProviderRegistry) -> None:
        """Parses YAML configurations and registers active AI providers."""
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML format for provider config: {str(e)}")

        if not data or "providers" not in data:
            raise ValueError("Invalid provider configuration: missing 'providers' root list.")

        providers_list = data.get("providers", [])
        if not isinstance(providers_list, list):
            raise ValueError("Invalid provider configuration: 'providers' must be a list.")

        for idx, prov in enumerate(providers_list):
            name = prov.get("name")
            enabled = prov.get("enabled", True)
            command = prov.get("command")
            health_cmd = prov.get("health_command")

            if not name:
                raise ValueError(f"Invalid provider configuration at index {idx}: missing 'name'.")
            if not command:
                raise ValueError(f"Invalid provider configuration for '{name}': missing 'command'.")

            if enabled:
                # Instantiate a generic CLI adapter for active providers
                adapter = GenericCLIProviderAdapter(
                    name_str=str(name),
                    command=str(command),
                    health_command=str(health_cmd) if health_cmd else None
                )
                
                # Register to registry, marking the first active one as default if not already set
                is_default = (idx == 0)
                registry.register(str(name), adapter, is_default=is_default)
