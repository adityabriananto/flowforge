import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from flowforge.ports.session_repository import EngineeringSessionRepository
from flowforge.domain.engineering_session import EngineeringSession, SessionMetadata, SessionStatus

class EngineeringSessionService:
    def __init__(self, repository: EngineeringSessionRepository):
        self.repository = repository

    def _assert_mutable(self, session: EngineeringSession) -> None:
        """Helper to verify that the session is not in a final state."""
        final_states = {SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED}
        if session.metadata.status in final_states:
            raise RuntimeError(
                f"Immutable Session: Cannot modify session '{session.metadata.session_id}' "
                f"because it is in a final state '{session.metadata.status.value}'."
            )

    def load_session(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        return self.repository.load(session_id, base_path)

    def save_session(self, session: EngineeringSession, base_path: str = ".") -> None:
        self.repository.save(session, base_path)

    def create_session(self, provider: str, mission: str, session_id: Optional[str] = None, base_path: str = ".") -> EngineeringSession:
        """Initializes a new Engineering Session in CREATED state."""
        s_id = session_id or str(uuid.uuid4())
        
        metadata = SessionMetadata(
            session_id=s_id,
            provider=provider,
            mission=mission,
            started_at=datetime.utcnow(),
            status=SessionStatus.CREATED
        )
        
        session = EngineeringSession(metadata=metadata)
        self.save_session(session, base_path)
        return session

    def start_session(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        """Transitions session status from CREATED to ACTIVE."""
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if session.metadata.status != SessionStatus.CREATED:
            raise ValueError(f"Invalid transition. Session '{session_id}' is in status '{session.metadata.status.value}', cannot start.")
            
        session.metadata.status = SessionStatus.ACTIVE
        self.save_session(session, base_path)
        return session

    def complete_session(self, session_id: str, summary: str, handover_summary: str, base_path: str = ".", state_service: Optional[Any] = None) -> EngineeringSession:
        """Transitions session status to COMPLETED and integrates results to Engineering State."""
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if session.metadata.status != SessionStatus.ACTIVE:
            raise ValueError(f"Invalid transition. Session '{session_id}' is in status '{session.metadata.status.value}', cannot complete.")
            
        session.metadata.status = SessionStatus.COMPLETED
        session.metadata.finished_at = datetime.utcnow()
        session.metadata.duration_seconds = (session.metadata.finished_at - session.metadata.started_at).total_seconds()
        session.summary = summary
        session.handover_summary = handover_summary
        
        self.save_session(session, base_path)
        
        # 1. Integrate with Engineering State if state_service is provided
        if state_service:
            # Sync active mission to completed if matching
            state_service.mark_mission_completed(session.metadata.mission, base_path=base_path)
            # Log provider usage
            state_service.update_provider(session.metadata.provider, base_path=base_path)
            # Sync knowledge references
            for art in session.artifacts:
                state_service.add_knowledge_reference(
                    title=f"Artifact generated during session {session_id}",
                    reference_path=art,
                    category="repository",
                    base_path=base_path
                )
            # Sync decisions
            for dec in session.decisions:
                state_service.add_decision(
                    title=dec.get("title", "Untitled Decision"),
                    rationale=dec.get("rationale", "No rationale"),
                    artifact_reference=dec.get("artifact_reference"),
                    base_path=base_path
                )
            # Sync blockers
            for blk in session.blockers:
                state_service.add_blocker(blk, base_path=base_path)
            # Sync recommendations
            for rec in session.recommendations:
                state_service.add_recommendation(rec, base_path=base_path)
                
        return session

    def fail_session(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        """Transitions session status to FAILED."""
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        session.metadata.status = SessionStatus.FAILED
        session.metadata.finished_at = datetime.utcnow()
        session.metadata.duration_seconds = (session.metadata.finished_at - session.metadata.started_at).total_seconds()
        
        self.save_session(session, base_path)
        return session

    def cancel_session(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        """Transitions session status to CANCELLED."""
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        session.metadata.status = SessionStatus.CANCELLED
        session.metadata.finished_at = datetime.utcnow()
        session.metadata.duration_seconds = (session.metadata.finished_at - session.metadata.started_at).total_seconds()
        
        self.save_session(session, base_path)
        return session

    def add_artifact(self, session_id: str, artifact_path: str, base_path: str = ".") -> EngineeringSession:
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if artifact_path not in session.artifacts:
            session.artifacts.append(artifact_path)
            
        self.save_session(session, base_path)
        return session

    def add_decision(self, session_id: str, title: str, rationale: str, artifact_reference: Optional[str] = None, base_path: str = ".") -> EngineeringSession:
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        decision = {
            "title": title,
            "rationale": rationale,
            "artifact_reference": artifact_reference,
            "decided_at": datetime.utcnow().isoformat()
        }
        session.decisions.append(decision)
        self.save_session(session, base_path)
        return session

    def add_warning(self, session_id: str, warning_text: str, base_path: str = ".") -> EngineeringSession:
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if warning_text not in session.warnings:
            session.warnings.append(warning_text)
            
        self.save_session(session, base_path)
        return session

    def add_blocker(self, session_id: str, blocker_text: str, base_path: str = ".") -> EngineeringSession:
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if blocker_text not in session.blockers:
            session.blockers.append(blocker_text)
            
        self.save_session(session, base_path)
        return session

    def add_recommendation(self, session_id: str, suggestion: str, base_path: str = ".") -> EngineeringSession:
        session = self.load_session(session_id, base_path)
        self._assert_mutable(session)
        
        if suggestion not in session.recommendations:
            session.recommendations.append(suggestion)
            
        self.save_session(session, base_path)
        return session

    def generate_handover(self, session_id: str, base_path: str = ".") -> Dict[str, Any]:
        """Assembles handover package containing decisions, remaining blockers, and next recommendations."""
        session = self.load_session(session_id, base_path)
        return {
            "session_id": session.metadata.session_id,
            "mission": session.metadata.mission,
            "status": session.metadata.status.value,
            "summary": session.summary,
            "artifacts_produced": session.artifacts,
            "decisions_made": [d["title"] for d in session.decisions],
            "files_modified": session.files_changed,
            "warnings_issued": session.warnings,
            "active_blockers": session.blockers,
            "suggested_next_steps": session.recommendations,
            "handover_summary": session.handover_summary
        }

    def export_session_summary(self, session_id: str, base_path: str = ".") -> str:
        """Generates a human-friendly string summary of the session results."""
        session = self.load_session(session_id, base_path)
        return f"""=== Engineering Session Summary [{session.metadata.session_id}] ===
Status: {session.metadata.status.value} (Provider: {session.metadata.provider})
Mission: {session.metadata.mission}
Started At: {session.metadata.started_at.isoformat()}
Finished At: {session.metadata.finished_at.isoformat() if session.metadata.finished_at else 'N/A'}
Duration: {session.metadata.duration_seconds or 0.0:.2f} seconds

Summary:
{session.summary or 'No summary provided.'}

Artifacts Produced:
{chr(10).join(f' - {art}' for art in session.artifacts) if session.artifacts else ' - None'}

Decisions Approved:
{chr(10).join(f" - {d['title']} ({d['rationale']})" for d in session.decisions) if session.decisions else ' - None'}

Active Blockers:
{chr(10).join(f' - {blk}' for blk in session.blockers) if session.blockers else ' - None'}

Suggested Next Steps:
{chr(10).join(f' - {rec}' for rec in session.recommendations) if session.recommendations else ' - None'}
"""
