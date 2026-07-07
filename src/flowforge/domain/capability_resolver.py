from typing import Dict, List, Optional
from flowforge.ports.connector import LlmConnector

class CapabilityResolver:
    def __init__(self, custom_mapping: Optional[Dict[str, List[str]]] = None):
        self.providers: Dict[str, LlmConnector] = {}
        # Dynamic fallback lists for LLM providers per capability
        self.capability_map: Dict[str, List[str]] = custom_mapping or {
            "architecture": ["claude", "gpt", "gemini"],
            "reasoning": ["claude", "gpt", "gemini"],
            "review": ["claude", "gpt", "gemini"],
            "coding": ["codex", "gpt", "qwen"],
            "autocomplete": ["codex", "gpt", "qwen"],
            "refactoring": ["codex", "gpt", "qwen"]
        }

    def register_provider(self, name: str, connector: LlmConnector) -> None:
        """Register an LLM connector provider instance (e.g. 'claude' or 'codex')."""
        self.providers[name.lower()] = connector

    def resolve_best_provider(self, capability: str) -> Optional[LlmConnector]:
        """
        Resolves the best available LLM connector based on the ordered list of fallback providers
        associated with the requested capability.
        """
        fallback_list = self.capability_map.get(capability.lower(), [])
        
        # Traverse the prioritized list and return the first registered/available provider
        for provider_name in fallback_list:
            provider_key = provider_name.lower()
            if provider_key in self.providers:
                return self.providers[provider_key]
        
        # Fallback to the first available provider if no fallback matches
        if self.providers:
            return list(self.providers.values())[0]
            
        return None
