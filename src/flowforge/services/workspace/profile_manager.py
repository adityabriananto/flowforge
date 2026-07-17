import os
import yaml
from typing import List, Optional
from flowforge.domain.provider_profile import ProfileConfig

class ProfileManager:
    @staticmethod
    def get_profiles_dir(base_path: str = ".") -> str:
        profiles_dir = os.path.join(base_path, ".flowforge", "profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        return profiles_dir

    @staticmethod
    def list_profiles(base_path: str = ".") -> List[ProfileConfig]:
        profiles_dir = ProfileManager.get_profiles_dir(base_path)
        profiles = []
        for file in os.listdir(profiles_dir):
            if file.endswith(".yaml"):
                try:
                    with open(os.path.join(profiles_dir, file), "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            profiles.append(ProfileConfig(**data))
                except Exception:
                    pass
        return sorted(profiles, key=lambda x: x.name)

    @staticmethod
    def add_profile(config: ProfileConfig, base_path: str = ".") -> None:
        profiles_dir = ProfileManager.get_profiles_dir(base_path)
        file_path = os.path.join(profiles_dir, f"{config.name}.yaml")
        
        data = {
            "name": config.name,
            "provider": config.provider,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
            
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

    @staticmethod
    def remove_profile(name: str, base_path: str = ".") -> bool:
        profiles_dir = ProfileManager.get_profiles_dir(base_path)
        file_path = os.path.join(profiles_dir, f"{name}.yaml")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_profile(name: str, base_path: str = ".") -> Optional[ProfileConfig]:
        profiles_dir = ProfileManager.get_profiles_dir(base_path)
        file_path = os.path.join(profiles_dir, f"{name}.yaml")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return ProfileConfig(**data) if data else None
            except Exception:
                pass
        return None
