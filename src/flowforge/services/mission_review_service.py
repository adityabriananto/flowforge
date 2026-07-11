from typing import Callable, Any
from flowforge.domain.mission import Mission
import yaml

class MissionReviewService:
    """
    Presents the drafted Mission to the developer for review before persistence.
    """
    
    def __init__(self, input_provider: Callable[[str], str] = input, print_provider: Callable[[Any], None] = print):
        self.input_provider = input_provider
        self.print_provider = print_provider

    def review_mission(self, mission: Mission) -> bool:
        """
        Displays the mission and asks for approval.
        Returns True if accepted, False if rejected or cancelled.
        """
        self.print_provider("\n" + "="*40)
        self.print_provider(" MISSION DRAFT REVIEW")
        self.print_provider("="*40)
        
        self.print_provider(f"Code: {mission.code}")
        self.print_provider(f"Title: {mission.title}")
        self.print_provider(f"Goal: {mission.goal}")
        self.print_provider(f"Priority: {mission.priority}")
        self.print_provider("\nDeliverables:")
        for d in mission.deliverables:
            self.print_provider(f"  - {d}")
            
        self.print_provider("\nConstraints:")
        for c in mission.constraints:
            self.print_provider(f"  - {c}")
            
        self.print_provider("\nDefinition of Done:")
        for dod in mission.definition_of_done:
            self.print_provider(f"  - {dod}")
            
        if mission.references:
            self.print_provider("\nReferences:")
            for ref in mission.references:
                self.print_provider(f"  - {ref}")
                
        self.print_provider("\nMetadata:")
        self.print_provider(yaml.dump(mission.metadata, default_flow_style=False).strip())
        
        self.print_provider("="*40)
        
        while True:
            choice = self.input_provider("Accept this mission? [y/N]: ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no', '']:
                return False
            else:
                self.print_provider("Please enter 'y' or 'n'.")
