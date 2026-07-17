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
        
        # Override context with mission metadata if available (resolves Bug #1 metadata loss)
        for key in ["framework", "language", "project_type"]:
            if mission.metadata.get(key) and mission.metadata.get(key) != "Unknown":
                selected_context[key] = mission.metadata[key]
                
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

        # Strengthen Deliverables
        deliverables = list(mission.deliverables)
        mandatory_deliverables = ["Source Code", "Unit Tests", "Documentation", "Execution Report", "Updated Project Status"]
        for md in mandatory_deliverables:
            if md not in deliverables:
                deliverables.append(md)

        # Strengthen Acceptance Criteria
        acceptance_criteria = [
            "Source code compiles and passes static analysis.",
            "Unit tests cover all new logic and pass successfully.",
            "Documentation reflects new changes accurately.",
            "Execution report clearly documents design decisions and validation."
        ]
        # Append original mapped ACs if they make sense, but for now we replace/strengthen.
        for d in mission.deliverables:
            acceptance_criteria.append(f"Deliverable '{d}' meets expected requirements and is verified.")

        # Strengthen Definition of Done
        definition_of_done = list(mission.definition_of_done)
        mandatory_dod = ["Source code implemented", "Tests passing", "Documentation updated", "Execution report generated", "Mission status updated"]
        for md in mandatory_dod:
            if md not in definition_of_done:
                definition_of_done.append(md)

        # Define Engineering Execution Contract
        execution_contract = {
            "required_outputs": [
                "source_code",
                "unit_tests",
                "documentation",
                "execution_report",
                "project_status_update"
            ],
            "reporting_instructions": [
                "1. Load engineering/templates/implementation_report.md.",
                "2. Complete every section defined in the template.",
                "3. Preserve all section headings.",
                "4. If a section is not applicable, write 'None' or 'Not Applicable'.",
                "5. Save the completed report to the configured report output location.",
                "6. Treat the report as a mandatory deliverable before marking the mission complete."
            ]
        }
        
        reporting = {
            "required": True,
            "purpose": "Provide implementation evidence.",
            "template_path": "engineering/templates/implementation_report.md",
            "required_sections": [
                "Executive Summary",
                "Scope",
                "Files Created",
                "Files Modified",
                "Technical Changes",
                "Validation Performed",
                "Backward Compatibility",
                "Known Limitations",
                "Completion Status"
            ],
            "execution_guidance": [
                "Every required section from the template must be present.",
                "Sections may contain 'None' or 'Not Applicable' when appropriate.",
                "Sections must never be omitted."
            ],
            "output_location": "engineering/reports/"
        }
        
        post_execution = [
            "update mission status",
            "update documentation",
            "load implementation report template",
            "update every required report section",
            "save engineering report",
            "validate report completeness"
        ]

        package_metadata = {
            "id": str(mission.id), # Using mission ID as package ID for now
            "compiler_version": get_version(),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace": os.path.basename(os.path.abspath(base_path)) or "unknown-workspace"
        }
        
        mission_metadata = {
            "id": str(mission.id),
            "code": mission.code,
            "title": mission.title
        }

        return MissionPackage(
            package=package_metadata,
            mission=mission_metadata,
            mission_summary=summary,
            objective=objective,
            deliverables=deliverables,
            constraints=constraints,
            relevant_rules=selected_rules,
            relevant_context=selected_context,
            relevant_references=selected_references,
            acceptance_criteria=acceptance_criteria,
            definition_of_done=definition_of_done,
            execution_contract=execution_contract,
            reporting=reporting,
            post_execution=post_execution,
            warnings=warnings
        )

