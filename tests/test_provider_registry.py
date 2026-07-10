import pytest
from flowforge.ports.ai_provider import AIProvider
from flowforge.services.runtime.provider_registry import AIRuntimeProviderRegistry
from flowforge.services.runtime.provider_config_loader import ProviderConfigLoader, GenericCLIProviderAdapter
from flowforge.domain.mission_package import MissionPackage
from flowforge.domain.engineering_state import EngineeringState
from flowforge.domain.mission import Mission

class DummyProvider(AIProvider):
    def __init__(self, provider_name: str):
        self._name = provider_name

    def name(self) -> str:
        return self._name

    def health(self) -> dict:
        return {"healthy": True}

    def execute(self, mission_package: MissionPackage, engineering_state: EngineeringState) -> dict:
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

def test_config_loader_success():
    yaml_config = """
providers:
  - name: "Claude"
    enabled: true
    command: "uv run python agents/coder.py"
    health_command: "ping api.anthropic.com"
  - name: "Ollama"
    enabled: true
    command: "ollama run model"
  - name: "Gemini"
    enabled: false
    command: "python gemini.py"
"""
    registry = AIRuntimeProviderRegistry()
    ProviderConfigLoader.load_from_yaml(yaml_config, registry)
    
    # Verify Claude & Ollama registered, Gemini ignored (enabled: false)
    assert "Claude" in registry.list()
    assert "Ollama" in registry.list()
    assert "Gemini" not in registry.list()
    
    claude_provider = registry.get("Claude")
    assert isinstance(claude_provider, GenericCLIProviderAdapter)
    assert claude_provider.name() == "Claude"
    assert claude_provider.command == "uv run python agents/coder.py"
    assert claude_provider.health_command == "ping api.anthropic.com"
    
    assert registry.default() == claude_provider

def test_config_loader_invalid_yaml():
    registry = AIRuntimeProviderRegistry()
    with pytest.raises(ValueError) as exc:
        ProviderConfigLoader.load_from_yaml("invalid: yaml: : format", registry)
    assert "Invalid YAML format" in str(exc.value)

def test_config_loader_missing_providers_root():
    registry = AIRuntimeProviderRegistry()
    with pytest.raises(ValueError) as exc:
        ProviderConfigLoader.load_from_yaml("version: 1", registry)
    assert "missing 'providers'" in str(exc.value)

def test_config_loader_missing_required_fields():
    registry = AIRuntimeProviderRegistry()
    
    # Missing name
    yaml_missing_name = """
providers:
  - enabled: true
    command: "python main.py"
"""
    with pytest.raises(ValueError) as exc:
        ProviderConfigLoader.load_from_yaml(yaml_missing_name, registry)
    assert "missing 'name'" in str(exc.value)

    # Missing command
    yaml_missing_cmd = """
providers:
  - name: "Claude"
    enabled: true
"""
    with pytest.raises(ValueError) as exc:
        ProviderConfigLoader.load_from_yaml(yaml_missing_cmd, registry)
    assert "missing 'command'" in str(exc.value)
