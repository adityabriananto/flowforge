from typing import Optional, Dict, Any, List
from flowforge.domain.mission import Mission
from flowforge.domain.agent_profile import AgentProfile
from flowforge.domain.mission_package import MissionPackage
from flowforge.services.compiler.context_selector import ContextSelector
from flowforge.services.compiler.rule_selector import RuleSelector
from flowforge.services.compiler.reference_collector import ReferenceCollector

class MissionPackageCompiler:
    def __init__(
        self, 
        rules_file_path: str = "engineering/decisions/AGENTS.md", 
        references_dir: str = "engineering/architecture"
    ):
        self.rules_file_path = rules_file_path
        self.references_dir = references_dir

    def compile(
        self,
        mission: Mission,
        agent_profile: Optional[AgentProfile] = None,
        project_context: Optional[Dict[str, Any]] = None,
        workflow_state: Optional[str] = None,
        sprint_status: Optional[str] = None,
        base_path: str = "."
    ) -> MissionPackage:
        """
        Compiles engineering inputs into a structured, vendor-agnostic MissionPackage.
        Processes context selection and rule selection based on keywords.
        """
        import os
        from datetime import datetime
        from flowforge.utils.version import get_version

        # 1. Derive keywords from mission title and goal
        keywords = [mission.title]
        if mission.goal:
            keywords.append(mission.goal)
        
        # Split keywords to individual words for broader coverage
        split_keywords = []
        for kw in keywords:
            split_keywords.extend([w.strip(",.()\"'") for w in kw.split() if len(w) > 3])

        # 2. Context Selection (with keywords filter)
        selected_context = ContextSelector.select_relevant_context(
            keywords=split_keywords,
            project_context=project_context or {},
            base_path=base_path
        )
        
        # Always preserve active runtime state parameters in final context
        if workflow_state:
            selected_context["workflow_state"] = workflow_state
        if sprint_status:
            selected_context["sprint_status"] = sprint_status

        # 3. Rule Selection
        selected_rules = RuleSelector.select_relevant_rules(
            keywords=split_keywords,
            rules_file_path=self.rules_file_path
        )

        warnings = []
        if not selected_rules:
            warnings.append("No matching engineering rules found.")

        # 4. Reference Collection
        selected_references = ReferenceCollector.collect_references(
            reference_keys=mission.references,
            references_dir=self.references_dir,
            base_path=base_path
        )

        # 5. Assemble Mission Package
        summary = f"Mission: {mission.title} (Status: {mission.status})"
        objective = mission.description or mission.title
        
        # Merge constraints from profile (e.g. limitations) if present
        constraints = list(mission.constraints)
        if agent_profile:
            constraints.extend([f"Agent limitation: {lim}" for lim in agent_profile.limitations])

        # Map deliverables to acceptance criteria intelligently
        acceptance_criteria = []
        for d in mission.deliverables:
            if "Report" in d or "Brief" in d:
                acceptance_criteria.append(f"{d} created")
            elif "Analysis" in d or "Overview" in d or "Summary" in d:
                acceptance_criteria.append(f"{d} completed")
            elif "Implementation" in d or "Suite" in d or "Update" in d or "Patch" in d:
                acceptance_criteria.append(f"{d} integrated and verified")
            else:
                acceptance_criteria.append(f"{d} verified")

        metadata = {
            "workspace": os.path.basename(os.path.abspath(base_path)) or "unknown-workspace",
            "compiler_version": get_version(),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        return MissionPackage(
            mission_summary=summary,
            objective=objective,
            deliverables=list(mission.deliverables),
            constraints=constraints,
            relevant_rules=selected_rules,
            relevant_context=selected_context,
            relevant_references=selected_references,
            acceptance_criteria=acceptance_criteria,
            definition_of_done=list(mission.definition_of_done),
            warnings=warnings,
            metadata=metadata
        )
