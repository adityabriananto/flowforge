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
        rules_file_path: str = "AGENTS.md", 
        references_dir: str = "docs/references"
    ):
        self.rules_file_path = rules_file_path
        self.references_dir = references_dir

    def compile(
        self,
        mission: Mission,
        agent_profile: Optional[AgentProfile] = None,
        project_context: Optional[Dict[str, Any]] = None,
        workflow_state: Optional[str] = None,
        sprint_status: Optional[str] = None
    ) -> MissionPackage:
        """
        Compiles engineering inputs into a structured, vendor-agnostic MissionPackage.
        Processes context selection and rule selection based on keywords.
        """
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
            project_context=project_context or {}
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

        # 4. Reference Collection
        selected_references = ReferenceCollector.collect_references(
            reference_keys=mission.references,
            references_dir=self.references_dir
        )

        # 5. Assemble Mission Package
        summary = f"Mission: {mission.title} (Status: {mission.status})"
        objective = mission.description or mission.title
        
        # Merge constraints from profile (e.g. limitations) if present
        constraints = list(mission.constraints)
        if agent_profile:
            constraints.extend([f"Agent limitation: {lim}" for lim in agent_profile.limitations])

        return MissionPackage(
            mission_summary=summary,
            objective=objective,
            deliverables=list(mission.deliverables),
            constraints=constraints,
            relevant_rules=selected_rules,
            relevant_context=selected_context,
            relevant_references=selected_references,
            acceptance_criteria=list(mission.deliverables),
            definition_of_done=list(mission.definition_of_done)
        )
