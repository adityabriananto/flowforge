import pytest
from flowforge.ports.ai_provider import AIProvider
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.domain.mission_package import MissionPackage
from flowforge.domain.mission import Mission

class DummyProvider(AIProvider):
    def __init__(self, provider_name: str):
        self._name = provider_name

    def name(self) -> str:
        return self._name

    def health(self) -> dict:
        return {"healthy": True}

    def execute(self, mission_package: MissionPackage, **kwargs) -> dict:
        return {"result": "success"}

def test_registry_registration_and_retrieval():
    registry = AIRuntimeProviderRegistry()
    claude = DummyProvider("Claude")
    gemini = DummyProvider("Gemini")
    
    registry.register("Claude", claude, is_default=True)
    registry.register("Gemini", gemini)
    
    assert registry.get("Claude") == claude
    assert registry.get("gemini") == gemini  # Case-insensitive resolution
    assert registry.default() == claude
    assert "Claude" in registry.list()
    assert "Gemini" in registry.list()

def test_registry_unregistered_error():
    registry = AIRuntimeProviderRegistry()
    with pytest.raises(KeyError) as exc:
        registry.get("Claude")
    assert "not registered" in str(exc.value)

def test_registry_no_default_provider():
    registry = AIRuntimeProviderRegistry()
    with pytest.raises(RuntimeError) as exc:
        registry.default()
    assert "No AI providers registered" in str(exc.value)
