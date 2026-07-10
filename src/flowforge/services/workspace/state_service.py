import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from flowforge.ports.state_repository import EngineeringStateRepository
from flowforge.domain.engineering_state import (
    EngineeringState,
    KnowledgeEntry,
    DecisionEntry,
    BlockerEntry,
    RecommendationEntry
)

class EngineeringStateService:
    def __init__(self, repository: EngineeringStateRepository):
        self.repository = repository

    def load_state(self, base_path: str = ".") -> EngineeringState:
        """Loads the current engineering state from the workspace repository."""
        return self.repository.load(base_path)

    def save_state(self, state: EngineeringState, base_path: str = ".") -> None:
        """Persists the engineering state to the workspace repository."""
        self.repository.save(state, base_path)

    def update_current_mission(self, mission_code: str, base_path: str = ".") -> EngineeringState:
        """Sets the currently active mission code, adding the old active one to history."""
        state = self.load_state(base_path)
        old_mission = state.mission.current_mission
        
        if old_mission and old_mission != mission_code:
            if old_mission not in state.mission.mission_history:
                state.mission.mission_history.append(old_mission)
                
        state.mission.current_mission = mission_code
        self.save_state(state, base_path)
        return state

    def mark_mission_completed(self, mission_code: str, base_path: str = ".") -> EngineeringState:
        """Marks a mission as completed, clearing it from active and logging history."""
        state = self.load_state(base_path)
        
        if state.mission.current_mission == mission_code:
            state.mission.current_mission = None
            
        if mission_code not in state.mission.completed_missions:
            state.mission.completed_missions.append(mission_code)
            
        if mission_code not in state.mission.mission_history:
            state.mission.mission_history.append(mission_code)
            
        self.save_state(state, base_path)
        return state

    def update_provider(self, provider_name: str, base_path: str = ".") -> EngineeringState:
        """Registers the current AI provider runtime and logs it into provider history."""
        state = self.load_state(base_path)
        old_provider = state.provider.current_provider
        
        if old_provider and old_provider != provider_name:
            if old_provider not in state.provider.provider_history:
                state.provider.provider_history.append(old_provider)
                
        state.provider.current_provider = provider_name
        self.save_state(state, base_path)
        return state

    def add_knowledge_reference(self, title: str, reference_path: str, base_path: str = ".") -> EngineeringState:
        """Adds a newly discovered engineering artifact or knowledge indexing to the state."""
        state = self.load_state(base_path)
        k_id = f"KNOW-{len(state.knowledge) + 1:03d}"
        
        entry = KnowledgeEntry(
            id=k_id,
            title=title,
            reference_path=reference_path,
            extracted_at=datetime.utcnow()
        )
        state.knowledge.append(entry)
        self.save_state(state, base_path)
        return state

    def add_decision(self, title: str, rationale: str, base_path: str = ".") -> EngineeringState:
        """Records an architectural or engineering decision."""
        state = self.load_state(base_path)
        d_id = f"DEC-{len(state.decisions) + 1:03d}"
        
        entry = DecisionEntry(
            id=d_id,
            title=title,
            rationale=rationale,
            decided_at=datetime.utcnow()
        )
        state.decisions.append(entry)
        self.save_state(state, base_path)
        return state

    def add_blocker(self, description: str, base_path: str = ".") -> EngineeringState:
        """Introduces an active blocker preventing engineering progress."""
        state = self.load_state(base_path)
        b_id = f"BLK-{len(state.blockers) + 1:03d}"
        
        entry = BlockerEntry(
            id=b_id,
            description=description,
            created_at=datetime.utcnow()
        )
        state.blockers.append(entry)
        self.save_state(state, base_path)
        return state

    def add_recommendation(self, suggestion: str, base_path: str = ".") -> EngineeringState:
        """Appends suggested next steps recommended by a completed execution."""
        state = self.load_state(base_path)
        r_id = f"REC-{len(state.recommendations) + 1:03d}"
        
        entry = RecommendationEntry(
            id=r_id,
            suggestion=suggestion,
            proposed_at=datetime.utcnow()
        )
        state.recommendations.append(entry)
        self.save_state(state, base_path)
        return state

    def resume_engineering_state(self, base_path: str = ".") -> Dict[str, Any]:
        """
        Restores complete context to resume engineering work without previous chat logs.
        Aggregates current state, active blockers, decisions, and target recommendations.
        """
        state = self.load_state(base_path)
        return {
            "project_name": state.project.name,
            "engineering_phase": state.workspace.engineering_phase,
            "active_mission": state.mission.current_mission,
            "active_blockers": [b.description for b in state.blockers],
            "recent_decisions": [(d.title, d.rationale) for d in state.decisions[-3:]],
            "next_suggestions": [r.suggestion for r in state.recommendations]
        }
