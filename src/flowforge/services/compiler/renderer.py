import yaml
from typing import Dict, Any
from flowforge.domain.mission_package import MissionPackage

class MissionPackageRenderer:
    @staticmethod
    def to_dict(package: MissionPackage) -> Dict[str, Any]:
        """Converts a MissionPackage dataclass to a dictionary representation."""
        return {
            "package": package.package,
            "mission": package.mission,
            "mission_summary": package.mission_summary,
            "objective": package.objective,
            "deliverables": package.deliverables,
            "constraints": package.constraints,
            "relevant_rules": package.relevant_rules,
            "relevant_context": package.relevant_context,
            "relevant_references": package.relevant_references,
            "acceptance_criteria": package.acceptance_criteria,
            "definition_of_done": package.definition_of_done,
            "warnings": package.warnings
        }

    @staticmethod
    def render_to_yaml(package: MissionPackage) -> str:
        """Serializes a MissionPackage into a vendor-agnostic YAML string representation."""
        data = MissionPackageRenderer.to_dict(package)
        return yaml.dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True)
