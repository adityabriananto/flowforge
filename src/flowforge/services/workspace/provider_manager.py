import os
import yaml
from typing import List, Optional
from flowforge.domain.provider_profile import ProviderConfig

class ProviderManager:
    @staticmethod
    def get_providers_dir(base_path: str = ".") -> str:
        providers_dir = os.path.join(base_path, ".flowforge", "providers")
        os.makedirs(providers_dir, exist_ok=True)
        return providers_dir

    @staticmethod
    def list_providers(base_path: str = ".") -> List[ProviderConfig]:
        providers_dir = ProviderManager.get_providers_dir(base_path)
        providers = []
        for file in os.listdir(providers_dir):
            if file.endswith(".yaml"):
                try:
                    with open(os.path.join(providers_dir, file), "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            providers.append(ProviderConfig(**data))
                except Exception:
                    pass
        return sorted(providers, key=lambda x: x.name)

    @staticmethod
    def add_provider(config: ProviderConfig, base_path: str = ".") -> None:
        providers_dir = ProviderManager.get_providers_dir(base_path)
        file_path = os.path.join(providers_dir, f"{config.name}.yaml")
        
        data = {
            "name": config.name,
            "provider": config.provider,
            "type": config.type
        }
        if config.model: data["model"] = config.model
        if config.api_key_env: data["api_key_env"] = config.api_key_env
        if config.endpoint: data["endpoint"] = config.endpoint
        if config.command: data["command"] = config.command
        if config.args: data["args"] = config.args
            
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

    @staticmethod
    def remove_provider(name: str, base_path: str = ".") -> bool:
        providers_dir = ProviderManager.get_providers_dir(base_path)
        file_path = os.path.join(providers_dir, f"{name}.yaml")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_provider(name: str, base_path: str = ".") -> Optional[ProviderConfig]:
        providers_dir = ProviderManager.get_providers_dir(base_path)
        file_path = os.path.join(providers_dir, f"{name}.yaml")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return ProviderConfig(**data) if data else None
            except Exception:
                pass
        return None
