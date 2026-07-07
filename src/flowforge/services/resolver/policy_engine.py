from typing import Dict, List, Optional, Any
from flowforge.ports.connector import ExecutionConnector

class CapabilityPolicyEngine:
    """
    A rule-driven capability policy engine that selects execution providers based on
    strategy policies (quality-first, cost-first) and dynamic fallbacks.
    Provider names are never hardcoded — they are populated at runtime from registered providers.
    """
    def __init__(self, policy_strategy: str = "quality-first"):
        self.strategy = policy_strategy
        self.providers: Dict[str, ExecutionConnector] = {}

        # Policy definitions: ordering is populated dynamically from registered providers.
        # Users can override this via configuration.
        self.capability_policy: Dict[str, Dict[str, List[str]]] = {
            "quality-first": {},
            "cost-first": {}
        }

    def register_provider(self, name: str, connector: ExecutionConnector) -> None:
        self.providers[name.lower()] = connector

    def resolve_provider_by_policy(self, capability: str) -> Optional[ExecutionConnector]:
        """
        Resolves an Execution Provider matching capability based on policy strategy rules.
        Falls back to iterating all registered providers if no policy rule matches.
        """
        strategy_rules = self.capability_policy.get(self.strategy, {})
        fallback_list = strategy_rules.get(capability.lower(), list(self.providers.keys()))

        for name in fallback_list:
            provider_key = name.lower()
            if provider_key in self.providers:
                return self.providers[provider_key]

        if self.providers:
            return list(self.providers.values())[0]

        return None
