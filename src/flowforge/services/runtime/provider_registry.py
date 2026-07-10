from typing import Dict, List, Optional
from flowforge.ports.ai_provider import AIProvider

class AIRuntimeProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        self._default_provider_name: Optional[str] = None

    def register(self, name: str, provider: AIProvider, is_default: bool = False) -> None:
        """Registers a new AI provider runtime plugin."""
        provider_name = name.strip().lower()
        self._providers[provider_name] = provider
        
        if is_default or self._default_provider_name is None:
            self._default_provider_name = provider_name

    def get(self, name: str) -> AIProvider:
        """Retrieves a registered AI provider by name."""
        provider_name = name.strip().lower()
        provider = self._providers.get(provider_name)
        if not provider:
            raise KeyError(f"AI Provider '{name}' is not registered in the runtime registry.")
        return provider

    def list(self) -> List[str]:
        """Lists names of all registered AI providers."""
        return [prov.name() for prov in self._providers.values()]

    def default(self) -> AIProvider:
        """Returns the default registered AI provider."""
        if not self._default_provider_name:
            raise RuntimeError("No AI providers registered in the registry. Cannot resolve default provider.")
        return self.get(self._default_provider_name)
