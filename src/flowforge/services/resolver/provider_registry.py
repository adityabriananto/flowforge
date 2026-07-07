import os
import re
from typing import Dict, Any, List, Optional
from flowforge.ports.connector import LlmConnector

def parse_yaml_fallback(content: str) -> Dict[str, Any]:
    """Helper regex parser for YAML provider files."""
    data = {}
    current_key = None
    lines = content.splitlines()
    for line in lines:
        line_clean = re.sub(r'#.*$', '', line).strip()
        if not line_clean:
            continue
        # Check subkey indentation block for capabilities
        if line.startswith("  ") and current_key == "capabilities":
            sub_match = re.match(r'^(\w+):\s*(\d+)$', line_clean)
            if sub_match:
                if "capabilities" not in data:
                    data["capabilities"] = {}
                data["capabilities"][sub_match.group(1)] = int(sub_match.group(2))
            continue
            
        match = re.match(r'^(\w+):\s*(.*?)$', line_clean)
        if match:
            key = match.group(1)
            val = match.group(2).strip("'\"")
            if key == "capabilities":
                data[key] = {}
            else:
                if val.isdigit():
                    val = int(val)
                data[key] = val
            current_key = key
            
    return data

class ProviderRegistry:
    """
    A Dynamic YAML Provider Registry that loads model profiles from providers/*.yaml 
    and resolves the best provider based on policy strategies (Challenge #16).
    """
    def __init__(self, providers_dir: Optional[str] = None):
        self.providers_dir = providers_dir or os.path.abspath(os.path.join(os.getcwd(), "providers"))
        self.provider_profiles: Dict[str, Dict[str, Any]] = {}
        self.connectors: Dict[str, LlmConnector] = {}

    def register_connector(self, name: str, connector: LlmConnector) -> None:
        """Associate an LLM Connector instance with a registered provider name."""
        self.connectors[name.lower()] = connector

    def load_profiles(self) -> None:
        """Scans providers/ directory and loads YAML profiles."""
        if not os.path.exists(self.providers_dir):
            return
            
        for file_name in os.listdir(self.providers_dir):
            if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                file_path = os.path.join(self.providers_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    try:
                        import yaml
                        profile = yaml.safe_load(content)
                    except ImportError:
                        profile = parse_yaml_fallback(content)
                        
                    name = profile.get("name", os.path.splitext(file_name)[0]).lower()
                    self.provider_profiles[name] = profile
                except Exception:
                    pass

    def resolve_by_policy(self, capability: str, strategy: str = "quality-first") -> Optional[LlmConnector]:
        """
        Dynamically calculates the best LLM provider matching capability using 
        weighted scoring based on strategy policy (quality-first / cost-first).
        """
        self.load_profiles()
        best_provider: Optional[str] = None
        best_score = -999999.0
        
        cost_weight = 100.0 if strategy == "cost-first" else 0.0
        quality_weight = 1.0 if strategy == "quality-first" else 0.2
        
        for name, profile in self.provider_profiles.items():
            if name not in self.connectors:
                continue
                
            caps = profile.get("capabilities", {})
            cap_score = caps.get(capability.lower(), 50)
            
            # Map cost category to numeric modifier
            cost_val = profile.get("cost", "medium").lower()
            if cost_val == "low":
                cost_score = 100.0
            elif cost_val == "medium":
                cost_score = 50.0
            else: # high
                cost_score = 0.0
                
            # Weighted utility function
            score = (quality_weight * cap_score) + (cost_weight * cost_score)
            
            if score > best_score:
                best_score = score
                best_provider = name
                
        if best_provider:
            return self.connectors[best_provider]
            
        # Fallback to first available connector
        if self.connectors:
            return list(self.connectors.values())[0]
            
        return None
