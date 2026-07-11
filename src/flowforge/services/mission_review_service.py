from typing import Callable, Any
from flowforge.domain.mission_draft import MissionDraft, MissionReviewAction
import yaml

class MissionReviewService:
    """
    Presents the drafted Mission to the developer for review before persistence.
    """
    
    def __init__(self, input_provider: Callable[[str], str] = input, print_provider: Callable[[Any], None] = print):
        self.input_provider = input_provider
        self.print_provider = print_provider

    def review_mission(self, draft: MissionDraft) -> MissionReviewAction:
        """
        Displays the mission draft and asks for approval.
        Returns the chosen MissionReviewAction.
        """
        self.print_provider("\n" + "="*40)
        self.print_provider(" Mission Draft")
        self.print_provider("="*40)
        
        self.print_provider("\nDeveloper Input")
        self.print_provider(f"- Mission Title: {draft.developer_input.title}")
        self.print_provider(f"- Business Goal: {draft.developer_input.business_goal}")
        self.print_provider(f"- Priority: {draft.developer_input.priority}")
        
        self.print_provider("\n" + "-"*40)
        self.print_provider("Planning Context")
        
        self.print_provider(f"\nProject:\n{draft.planning_context.project_name}")
        self.print_provider(f"\nFramework:\n{draft.planning_context.framework}")
        self.print_provider(f"\nLanguage:\n{draft.planning_context.language}")
        self.print_provider(f"\nProject Type:\n{draft.planning_context.project_type}")
        self.print_provider(f"\nCurrent Phase:\n{draft.planning_context.current_phase}")
        
        self.print_provider("\nCompleted Missions:")
        if draft.planning_context.completed_missions:
            for m in draft.planning_context.completed_missions:
                self.print_provider(m)
        else:
            self.print_provider("None")
        
        self.print_provider("\n" + "-"*40)
        self.print_provider("Generated Mission")
        
        self.print_provider("\nObjective:")
        self.print_provider(draft.generated_mission.goal)
        
        self.print_provider("\nExpected Engineering Outputs:")
        for d in draft.generated_mission.deliverables:
            self.print_provider(f"  - {d}")
            
        self.print_provider("\nConstraints:")
        for c in draft.generated_mission.constraints:
            self.print_provider(f"  - {c}")
            
        self.print_provider("\nDefinition of Done:")
        for dod in draft.generated_mission.definition_of_done:
            self.print_provider(f"  - {dod}")
            
        if draft.generated_mission.references:
            self.print_provider("\nReferences:")
            for ref in draft.generated_mission.references:
                self.print_provider(f"  - {ref}")
        
        self.print_provider("\n" + "="*40)
        self.print_provider("Actions")
        self.print_provider("[A] Accept")
        self.print_provider("[E] Edit")
        self.print_provider("[C] Cancel")
        self.print_provider("="*40)
        
        while True:
            choice = self.input_provider("Select an action [A/E/C]: ").strip().lower()
            if choice == 'a':
                return MissionReviewAction.ACCEPT
            elif choice == 'e':
                return MissionReviewAction.EDIT
            elif choice == 'c':
                return MissionReviewAction.CANCEL
            else:
                self.print_provider("Please enter 'A', 'E', or 'C'.")
