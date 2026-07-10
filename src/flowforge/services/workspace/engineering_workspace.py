import os
import shutil
from typing import List

class EngineeringWorkspace:
    """
    Standardizes the FlowForge directory layout by separating editable engineering source files
    (engineering/) from runtime generated assets (.flowforge/).
    """
    
    ENGINEERING_DIRS = [
        "engineering/missions/backlog",
        "engineering/missions/active",
        "engineering/missions/completed",
        "engineering/missions/templates",
        "engineering/rfcs",
        "engineering/adrs",
        "engineering/roadmap",
        "engineering/architecture",
        "engineering/decisions"
    ]
    
    FLOWFORGE_DIRS = [
        ".flowforge/packages",
        ".flowforge/cache",
        ".flowforge/workspace",
        ".flowforge/logs"
    ]

    @classmethod
    def initialize_workspace(cls, base_path: str = ".") -> None:
        """Creates the standardized folder hierarchy under base_path."""
        # 1. Create Engineering Directories
        for directory in cls.ENGINEERING_DIRS:
            path = os.path.join(base_path, directory)
            os.makedirs(path, exist_ok=True)
            
        # 2. Create Runtime Directories
        for directory in cls.FLOWFORGE_DIRS:
            path = os.path.join(base_path, directory)
            os.makedirs(path, exist_ok=True)

    @classmethod
    def move_mission_file(
        cls, 
        filename: str, 
        from_state: str, 
        to_state: str, 
        base_path: str = "."
    ) -> str:
        """
        Transitions a mission YAML file across backlog, active, or completed states.
        Raises FileNotFoundError if source file is missing.
        """
        valid_states = {"backlog", "active", "completed"}
        from_state = from_state.strip().lower()
        to_state = to_state.strip().lower()

        if from_state not in valid_states or to_state not in valid_states:
            raise ValueError(f"Invalid state transition. Must be one of {valid_states}")

        src_dir = os.path.join(base_path, "engineering", "missions", from_state)
        dest_dir = os.path.join(base_path, "engineering", "missions", to_state)
        
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if not os.path.exists(src_file):
            raise FileNotFoundError(f"Source mission file '{filename}' not found in '{from_state}' folder.")

        # Ensure destination exists
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(src_file, dest_file)
        return dest_file
