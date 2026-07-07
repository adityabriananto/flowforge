from typing import Dict, List, Optional
from flowforge.ports.connector import LlmConnector
from flowforge.services.resolver.policy_engine import CapabilityPolicyEngine

class CapabilityResolver:
    def __init__(self, custom_mapping: Optional[Dict[str, List[str]]] = None):
        self.providers: Dict[str, LlmConnector] = {}
        self.capability_map: Dict[str, List[str]] = custom_mapping or {
            "architecture": ["claude", "gpt", "gemini"],
            "reasoning": ["claude", "gpt", "gemini"],
            "review": ["claude", "gpt", "gemini"],
            "coding": ["codex", "gpt", "qwen"],
            "autocomplete": ["codex", "gpt", "qwen"],
            "refactoring": ["codex", "gpt", "qwen"]
        }

    def register_provider(self, name: str, connector: LlmConnector) -> None:
        self.providers[name.lower()] = connector

    def resolve_best_provider(self, capability: str) -> Optional[LlmConnector]:
        fallback_list = self.capability_map.get(capability.lower(), [])
        for provider_name in fallback_list:
            provider_key = provider_name.lower()
            if provider_key in self.providers:
                return self.providers[provider_key]
        if self.providers:
            return list(self.providers.values())[0]
        return None
