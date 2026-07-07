from typing import Dict, Any, Optional
from flowforge.ports.connector import LlmConnector

class CapabilityResolver:
    def __init__(self):
        self.providers: Dict[str, LlmConnector] = {}
        # Mapping capabilities to preferred provider name
        self.capability_map: Dict[str, str] = {
            "architecture": "claude",
            "reasoning": "claude",
            "review": "claude",
            "coding": "codex",
            "autocomplete": "codex",
            "refactoring": "codex"
        }

    def register_provider(self, name: str, connector: LLMConnector) -> None:
        """Register an LLM connector provider instance (e.g. 'claude' or 'codex')."""
        self.providers[name.lower()] = connector

    def resolve_best_provider(self, capability: str) -> Optional[LLMConnector]:
        """
        Resolves the best available registered LLM connector provider 
        for a given capability request.
        """
        provider_name = self.capability_map.get(capability.lower())
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        # Fallback to first available provider if the mapping doesn't exist
        if self.providers:
            return list(self.providers.values())[0]
            
        return None
