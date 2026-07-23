from typing import Optional, List, Dict, Any
from flowforge.ports.mission_repository import MissionRepository
from flowforge.services.artifact_identity_service import ArtifactIdentityService
from flowforge.domain.mission import Mission
from flowforge.services.planning_context_builder import PlanningContextBuilder
from flowforge.services.mission_planning_engine import MissionPlanningEngine
from flowforge.services.mission_review_service import MissionReviewService

class MissionCreationService:
    """
    Orchestrates the new Mission Authoring workflow:
    Identity -> Context -> Planning -> Review -> Repository.save
    """
    def __init__(
        self, 
        repository: MissionRepository, 
        base_path: str = ".",
        review_service: Optional[MissionReviewService] = None
    ):
        self.repository = repository
        self.base_path = base_path
        self.context_builder = PlanningContextBuilder(base_path)
        self.planning_engine = MissionPlanningEngine()
        self.review_service = review_service or MissionReviewService()

    def _prompt_input(self, prompt_text: str, current_val: Optional[str] = None) -> str:
        # Helper to get user input from the console directly during the wizard.
        # In a real CLI, we might use richer interactive prompts, but simple input() works.
        prompt = f"{prompt_text} [{current_val}]: " if current_val else f"{prompt_text}: "
        val = input(prompt).strip()
        return val if val else (current_val or "")

    def _validate_priority(self, p: str) -> str:
        p = p.strip(" \t\n\r\"'").lower()
        if p in ["low", "medium", "high"]:
            return p
        return ""

    async def create_mission(
        self,
        title: Optional[str] = None,
        goal: Optional[str] = None,
        context: Optional[str] = None,
        users: Optional[str] = None,
        priority: Optional[str] = None,
        prefix: str = "PROJECT",
        notes: Optional[str] = None,
        auto_accept: bool = False
    ) -> Optional[Mission]:
        from flowforge.domain.mission_draft import DeveloperInput, MissionDraft, MissionReviewAction

        existing_identifiers = await self.repository.list_identifiers()
        next_code = ArtifactIdentityService.generate_next_identity(prefix, existing_identifiers)
        context_obj = self.context_builder.build_context()

        # Wizard State
        current_title = title or ""
        current_goal = goal or ""
        current_context = context or ""
        current_users = users or ""
        current_priority = (priority or "").lower()
        if not self._validate_priority(current_priority):
            current_priority = ""

        # Non-interactive mode check
        is_interactive = not (title and goal and context and users and self._validate_priority(priority or ""))

        while True:
            if is_interactive:
                print("\n" + "-"*40)
                print(" Mission Authoring Wizard")
                print("-"*40)
                while not current_title:
                    current_title = self._prompt_input("Mission Title", current_title)
                    if not current_title:
                        print("Error: Title is required.")
                
                while not current_goal:
                    current_goal = self._prompt_input("Project Goal", current_goal)
                    if not current_goal:
                        print("Error: Project Goal is required.")
                        
                while not current_context:
                    current_context = self._prompt_input("Business Context", current_context)
                    if not current_context:
                        print("Error: Business Context is required.")
                        
                while not current_users:
                    current_users = self._prompt_input("Target Users", current_users)
                    if not current_users:
                        print("Error: Target Users is required.")
                
                while not current_priority:
                    p = self._prompt_input("Priority (Low/Medium/High)", current_priority)
                    validated_p = self._validate_priority(p)
                    if validated_p:
                        current_priority = validated_p
                    else:
                        print("Error: Priority must be Low, Medium, or High.")
                
                print("-"*40 + "\n")

            dev_input = DeveloperInput(
                title=current_title, 
                project_goal=current_goal,
                business_context=current_context,
                target_users=current_users,
                priority=current_priority
            )
            
            generated_mission = self.planning_engine.generate_draft(
                context=context_obj,
                developer_input=dev_input,
                code=next_code,
                notes=notes
            )
            
            draft = MissionDraft(
                developer_input=dev_input,
                planning_context=context_obj,
                generated_mission=generated_mission
            )
            
            if auto_accept:
                action = MissionReviewAction.ACCEPT
            else:
                action = self.review_service.review_mission(draft)
            
            if action == MissionReviewAction.ACCEPT:
                await self.repository.save(generated_mission)
                return generated_mission
            elif action == MissionReviewAction.EDIT:
                is_interactive = True
                # Clear them out so the user can be prompted again, or leave them as defaults for the prompt
                print("\n--- Editing Developer Input ---")
                current_title = self._prompt_input("Mission Title", current_title)
                current_goal = self._prompt_input("Project Goal", current_goal)
                current_context = self._prompt_input("Business Context", current_context)
                current_users = self._prompt_input("Target Users", current_users)
                
                new_p = ""
                while not new_p:
                    p = self._prompt_input("Priority (Low/Medium/High)", current_priority)
                    validated_p = self._validate_priority(p)
                    if validated_p:
                        new_p = validated_p
                    else:
                        print("Error: Priority must be Low, Medium, or High.")
                current_priority = new_p
                continue
            elif action == MissionReviewAction.CANCEL:
                return None
