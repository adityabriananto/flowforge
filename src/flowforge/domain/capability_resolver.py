from typing import Dict, List, Optional
from flowforge.ports.connector import ExecutionConnector
from flowforge.services.resolver.policy_engine import CapabilityPolicyEngine

class CapabilityResolver:
    def __init__(self, custom_mapping: Optional[Dict[str, List[str]]] = None):
        self.providers: Dict[str, ExecutionConnector] = {}
        self.capability_map: Dict[str, List[str]] = custom_mapping or {}

    def register_provider(self, name: str, connector: ExecutionConnector) -> None:
        self.providers[name.lower()] = connector

    def resolve_best_provider(self, capability: str) -> Optional[ExecutionConnector]:
        fallback_list = self.capability_map.get(capability.lower(), list(self.providers.keys()))
        for provider_name in fallback_list:
            provider_key = provider_name.lower()
            if provider_key in self.providers:
                return self.providers[provider_key]
        if self.providers:
            return list(self.providers.values())[0]
        return None
