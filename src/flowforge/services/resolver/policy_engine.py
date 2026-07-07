from typing import Dict, List, Optional, Any
from flowforge.ports.connector import LlmConnector

class CapabilityPolicyEngine:
    """
    A rule-driven capability policy engine that selects LLM providers based on strategy policies
    (quality-first, cost-first) and fallbacks (Challenge #2 & Priority 3).
    """
    def __init__(self, policy_strategy: str = "quality-first"):
        self.strategy = policy_strategy
        self.providers: Dict[str, LlmConnector] = {}
        
        # Policy definitions (strategy mapping)
        self.capability_policy = {
            "quality-first": {
                "architecture": ["claude", "gpt", "gemini"],
                "coding": ["claude", "codex", "gpt"],
                "review": ["claude", "gpt"]
            },
            "cost-first": {
                "architecture": ["gemini", "gpt", "claude"],
                "coding": ["qwen", "codex", "gpt"],
                "review": ["gpt", "claude"]
            }
        }

    def register_provider(self, name: str, connector: LlmConnector) -> None:
        self.providers[name.lower()] = connector

    def resolve_provider_by_policy(self, capability: str) -> Optional[LlmConnector]:
        """
        Resolves LLM Provider matching capability based on policy strategy rules.
        """
        strategy_rules = self.capability_policy.get(self.strategy, self.capability_policy["quality-first"])
        fallback_list = strategy_rules.get(capability.lower(), ["claude", "gpt", "gemini"])
        
        for name in fallback_list:
            provider_key = name.lower()
            if provider_key in self.providers:
                return self.providers[provider_key]
                
        if self.providers:
            return list(self.providers.values())[0]
            
        return None
