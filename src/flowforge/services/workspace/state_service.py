import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from flowforge.ports.state_repository import EngineeringStateRepository
from flowforge.domain.engineering_state import (
    EngineeringState,
    ProviderUsage,
    KnowledgeEntry,
    DecisionEntry,
    EngineeringEvent,
    OpenQuestion,
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

    def _log_event(self, state: EngineeringState, event_type: str, description: str) -> None:
        """Helper to append an engineering event to the timeline log."""
        ev_id = f"EV-{len(state.timeline_state.event_log) + 1:03d}"
        state.timeline_state.event_log.append(EngineeringEvent(
            id=ev_id,
            event_type=event_type,
            description=description,
            timestamp=datetime.utcnow()
        ))

    def update_current_mission(self, mission_code: str, base_path: str = ".") -> EngineeringState:
        """Sets the currently active mission code, logs the timeline event, and updates histories."""
        state = self.load_state(base_path)
        old_mission = state.mission.current_mission
        
        if old_mission and old_mission != mission_code:
            if old_mission not in state.mission.mission_history:
                state.mission.mission_history.append(old_mission)
                
        state.mission.current_mission = mission_code
        self._log_event(state, "Mission Started", f"Started mission: {mission_code}")
        self.save_state(state, base_path)
        return state

    def mark_mission_completed(self, mission_code: str, base_path: str = ".") -> EngineeringState:
        """Marks a mission as completed, updates history, and records the timeline event."""
        state = self.load_state(base_path)
        
        if state.mission.current_mission == mission_code:
            state.mission.current_mission = None
            
        if mission_code not in state.mission.completed_missions:
            state.mission.completed_missions.append(mission_code)
            
        if mission_code not in state.mission.mission_history:
            state.mission.mission_history.append(mission_code)
            
        # Log completed provider usages
        for usage in state.provider.provider_history:
            if usage.mission == mission_code and not usage.finished_at:
                usage.finished_at = datetime.utcnow()

        self._log_event(state, "Mission Completed", f"Completed mission: {mission_code}")
        self.save_state(state, base_path)
        return state

    def update_provider(self, provider_name: str, base_path: str = ".") -> EngineeringState:
        """Registers the current AI provider runtime and tracks detailed ProviderUsage."""
        state = self.load_state(base_path)
        old_provider = state.provider.current_provider
        active_mission = state.mission.current_mission
        
        # Stop last usage
        if old_provider:
            for usage in state.provider.provider_history:
                if usage.provider == old_provider and not usage.finished_at:
                    usage.finished_at = datetime.utcnow()

        # Add new usage
        new_usage = ProviderUsage(
            provider=provider_name,
            mission=active_mission,
            started_at=datetime.utcnow()
        )
        state.provider.provider_history.append(new_usage)
        state.provider.current_provider = provider_name
        
        self._log_event(state, "Provider Changed", f"Switched AI Provider to: {provider_name}")
        self.save_state(state, base_path)
        return state

    def add_knowledge_reference(self, title: str, reference_path: str, category: str = "repository", base_path: str = ".") -> EngineeringState:
        """Adds a newly structured engineering artifact reference to the state."""
        state = self.load_state(base_path)
        k_id = f"KNOW-{len(state.knowledge_state.knowledge) + 1:03d}"
        
        entry = KnowledgeEntry(
            id=k_id,
            title=title,
            reference_path=reference_path,
            category=category,
            extracted_at=datetime.utcnow()
        )
        state.knowledge_state.knowledge.append(entry)
        self._log_event(state, "Artifact Generated", f"Registered knowledge reference: {title} ({category})")
        self.save_state(state, base_path)
        return state

    def add_decision(self, title: str, rationale: str, artifact_reference: Optional[str] = None, base_path: str = ".") -> EngineeringState:
        """Records an architectural or engineering decision."""
        state = self.load_state(base_path)
        d_id = f"DEC-{len(state.decision_state.decisions) + 1:03d}"
        active_mission = state.mission.current_mission
        
        entry = DecisionEntry(
            id=d_id,
            title=title,
            rationale=rationale,
            mission=active_mission,
            artifact_reference=artifact_reference,
            decided_at=datetime.utcnow()
        )
        state.decision_state.decisions.append(entry)
        self._log_event(state, "Decision Approved", f"Approved decision: {title}")
        self.save_state(state, base_path)
        return state

    def add_open_question(self, title: str, description: str, base_path: str = ".") -> EngineeringState:
        """Adds an unresolved engineering question to track blockers or research items."""
        state = self.load_state(base_path)
        oq_id = f"QST-{len(state.open_questions) + 1:03d}"
        active_mission = state.mission.current_mission
        
        entry = OpenQuestion(
            id=oq_id,
            title=title,
            description=description,
            mission=active_mission,
            status="open",
            created_at=datetime.utcnow()
        )
        state.open_questions.append(entry)
        self.save_state(state, base_path)
        return state

    def resolve_open_question(self, question_id: str, base_path: str = ".") -> EngineeringState:
        """Resolves a pending open question."""
        state = self.load_state(base_path)
        for oq in state.open_questions:
            if oq.id == question_id:
                oq.status = "resolved"
                oq.resolved_at = datetime.utcnow()
                
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

    def build_resume_context(self, base_path: str = ".") -> Dict[str, Any]:
        """
        Builds a comprehensive provider-independent context to resume work without history logs.
        Aggregates active missions, blockers, decisions, knowledge indexing, and open questions.
        """
        state = self.load_state(base_path)
        
        # Latest 3 decisions
        recent_decisions = [
            {
                "id": d.id,
                "title": d.title,
                "rationale": d.rationale,
                "mission": d.mission,
                "artifact": d.artifact_reference
            } for d in state.decision_state.decisions[-3:]
        ]
        
        # Open questions
        open_q = [
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "status": q.status
            } for q in state.open_questions if q.status == "open"
        ]
        
        # Knowledge index grouped or categorized
        knowledge_refs = [
            {
                "id": k.id,
                "title": k.title,
                "category": k.category,
                "path": k.reference_path
            } for k in state.knowledge_state.knowledge
        ]

        return {
            "project_name": state.project.name,
            "engineering_phase": state.workspace.engineering_phase,
            "current_mission": state.mission.current_mission,
            "completed_missions": state.mission.completed_missions,
            "active_blockers": [b.description for b in state.blockers],
            "latest_decisions": recent_decisions,
            "open_questions": open_q,
            "recommendations": [r.suggestion for r in state.recommendations],
            "engineering_knowledge": knowledge_refs
        }
