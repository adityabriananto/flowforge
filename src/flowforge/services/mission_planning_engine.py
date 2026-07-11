from typing import List, Dict, Any, Optional
from flowforge.domain.mission import Mission, MissionState
from flowforge.services.planning_context_builder import PlanningContext
from flowforge.domain.mission_factory import MissionFactory

class MissionPlanningEngine:
    """
    Deterministically generates Mission drafts based on Engineering Workspace knowledge.
    This component serves as the core base implementation. Future AI-assisted
    planning modules can extend or wrap this engine without modifying the Core.
    """
    
    def generate_draft(
        self,
        context: PlanningContext,
        title: str,
        goal: str,
        priority: str,
        code: str,
        notes: Optional[str] = None
    ) -> Mission:
        
        # Deterministic Rules
        deliverables = self._determine_deliverables(context, goal)
        constraints = self._determine_constraints(context)
        definition_of_done = self._determine_dod(context)
        
        metadata = {
            "framework": context.framework,
            "language": context.language,
            "project_type": context.project_type,
            "estimated_size": self._estimate_size(deliverables),
            "risk_level": "medium",
            "dependencies": []
        }
        
        if notes:
            metadata["developer_notes"] = notes
            
        mission = MissionFactory.create(
            title=title,
            description=goal,
            code=code,
            goals=[goal],
            metadata=metadata,
            priority=priority
        )
        
        mission.goal = goal
        mission.deliverables = deliverables
        mission.constraints = constraints
        mission.definition_of_done = definition_of_done
        mission.references = context.recent_adrs + context.recent_rfcs
        
        return mission

    def _determine_deliverables(self, context: PlanningContext, goal: str) -> List[str]:
        base = ["Implement core logic for: " + goal]
        
        if context.project_type in ["backend", "api"]:
            base.append("Create or update API endpoints")
            base.append("Write backend unit tests")
        elif context.project_type == "frontend":
            base.append("Build responsive UI components")
            base.append("Write frontend component tests")
            
        base.append("Update related documentation (STATUS, ROADMAP)")
        return base

    def _determine_constraints(self, context: PlanningContext) -> List[str]:
        constraints = [
            "Maintain backward compatibility",
            "Follow Clean Architecture principles",
            "Adhere to SOLID design principles"
        ]
        
        if context.language != "unknown":
            constraints.append(f"Follow idiomatic {context.language} patterns")
            
        if context.framework != "unknown":
            constraints.append(f"Ensure compatibility with {context.framework} best practices")
            
        return constraints

    def _determine_dod(self, context: PlanningContext) -> List[str]:
        return [
            "All unit and integration tests pass (100% success rate)",
            "Code successfully compiles without errors or warnings",
            "No new security vulnerabilities introduced",
            "Code has been reviewed against constraints",
            "Documentation is fully updated"
        ]

    def _estimate_size(self, deliverables: List[str]) -> str:
        if len(deliverables) <= 3:
            return "Small"
        elif len(deliverables) <= 5:
            return "Medium"
        return "Large"
