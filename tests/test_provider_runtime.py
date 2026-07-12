import pytest
from flowforge.ports.ai_provider import AIProvider
from flowforge.services.runtime.provider_config_loader import GenericCLIProviderAdapter
from flowforge.domain.mission_package import MissionPackage

def test_generic_cli_provider_adapter_compliance():
    adapter = GenericCLIProviderAdapter(
        name_str="TestClaude",
        command="python code.py",
        health_command="curl example.com"
    )
    
    assert adapter.name() == "TestClaude"
    assert adapter.health()["healthy"] is True
    
    # Create empty dummy inputs for validation
    mission_package = MissionPackage(
        mission_summary="Optimize Database",
        objective="Setup indices",
        deliverables=[],
        constraints=[],
        relevant_rules=[],
        relevant_context={},
        relevant_references=[]
    )
    
    res = adapter.execute(mission_package)
    
    # Assert canonical ExecutionResult schema keys exist
    assert res["status"] == "SUCCESS"
    assert "summary" in res
    assert "artifacts" in res
    assert "decisions" in res
    assert "files_changed" in res
    assert "warnings" in res
    assert "blockers" in res
    assert "recommendations" in res
    assert "handover_summary" in res
    assert res["provider_metadata"]["provider"] == "TestClaude"
    assert res["provider_metadata"]["command_executed"] == "python code.py"

def test_provider_interface_subclassing():
    # Verify that a custom provider can be easily implemented and passes typechecks
    class CustomGemini(AIProvider):
        def name(self) -> str:
            return "Gemini"
        def health(self) -> dict:
            return {"healthy": True}
        def execute(self, mission_package: MissionPackage, **kwargs) -> dict:
            return {"status": "SUCCESS"}
            
    gemini = CustomGemini()
    assert isinstance(gemini, AIProvider)
    assert gemini.name() == "Gemini"
