import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List
from flowforge.domain.engineering_state import (
    EngineeringState,
    ProjectState,
    WorkspaceState,
    MissionState,
    ProviderUsage,
    ProviderState,
    SessionState,
    KnowledgeEntry,
    KnowledgeState,
    DecisionEntry,
    DecisionState,
    EngineeringEvent,
    TimelineState,
    OpenQuestion,
    BlockerEntry,
    RecommendationEntry
)

class EngineeringStateLoader:
    @classmethod
    def load_from_yaml(cls, yaml_content: str) -> EngineeringState:
        """Parses YAML content and constructs a validated EngineeringState domain model."""
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")

        if not data:
            raise ValueError("Empty or invalid EngineeringState YAML content")

        # 1. Version Validation
        version = str(data.get("version", "1"))
        if version != "1":
            raise ValueError(f"Unsupported EngineeringState version '{version}'. Only version '1' is supported.")

        # 2. Parse Project
        proj_data = data.get("project", {})
        project = ProjectState(
            id=str(proj_data.get("id", "")),
            name=str(proj_data.get("name", "Unnamed Project"))
        )

        # 3. Parse Workspace
        ws_data = data.get("workspace", {})
        workspace = WorkspaceState(
            version=str(ws_data.get("version", "1")),
            engineering_phase=str(ws_data.get("engineering_phase", "init"))
        )

        # 4. Parse Mission State
        m_data = data.get("mission", {})
        mission = MissionState(
            current_mission=m_data.get("current_mission"),
            completed_missions=list(m_data.get("completed_missions", [])),
            mission_history=list(m_data.get("mission_history", []))
        )

        # Helper to parse datetime safely
        def parse_dt(dt_str: Any) -> datetime:
            if not dt_str:
                return datetime.utcnow()
            try:
                return datetime.fromisoformat(str(dt_str))
            except ValueError:
                return datetime.utcnow()

        # Helper to parse optional datetime safely
        def parse_optional_dt(dt_str: Any) -> Optional[datetime]:
            if not dt_str:
                return None
            try:
                return datetime.fromisoformat(str(dt_str))
            except ValueError:
                return None

        # 5. Parse Provider State (ProviderUsage)
        p_data = data.get("provider", {})
        provider_history = []
        for usage in p_data.get("provider_history", []) or []:
            provider_history.append(ProviderUsage(
                provider=str(usage.get("provider", "")),
                mission=usage.get("mission"),
                started_at=parse_dt(usage.get("started_at")),
                finished_at=parse_optional_dt(usage.get("finished_at"))
            ))
        provider = ProviderState(
            current_provider=p_data.get("current_provider"),
            provider_history=provider_history
        )

        # 6. Parse Session State
        s_data = data.get("session", {})
        session = SessionState(
            current_session_id=s_data.get("current_session_id"),
            latest_session_id=s_data.get("latest_session_id")
        )

        # 7. Parse Knowledge State
        k_data = data.get("knowledge_state", {})
        knowledge = []
        for k in k_data.get("knowledge", []) or []:
            knowledge.append(KnowledgeEntry(
                id=str(k.get("id", "")),
                title=str(k.get("title", "")),
                reference_path=str(k.get("reference_path", "")),
                category=str(k.get("category", "repository")),
                extracted_at=parse_dt(k.get("extracted_at"))
            ))
        knowledge_state = KnowledgeState(knowledge=knowledge)

        # 8. Parse Decisions State
        d_data = data.get("decision_state", {})
        decisions = []
        for d in d_data.get("decisions", []) or []:
            decisions.append(DecisionEntry(
                id=str(d.get("id", "")),
                title=str(d.get("title", "")),
                rationale=str(d.get("rationale", "")),
                mission=d.get("mission"),
                artifact_reference=d.get("artifact_reference"),
                decided_at=parse_dt(d.get("decided_at"))
            ))
        decision_state = DecisionState(decisions=decisions)

        # 9. Parse Timeline State (EngineeringEvent)
        t_data = data.get("timeline_state", {})
        event_log = []
        for ev in t_data.get("event_log", []) or []:
            event_log.append(EngineeringEvent(
                id=str(ev.get("id", "")),
                event_type=str(ev.get("event_type", "Engineering State Updated")),
                description=str(ev.get("description", "")),
                timestamp=parse_dt(ev.get("timestamp"))
            ))
        timeline_state = TimelineState(event_log=event_log)

        # 10. Parse Open Questions
        open_questions = []
        for oq in data.get("open_questions", []) or []:
            open_questions.append(OpenQuestion(
                id=str(oq.get("id", "")),
                title=str(oq.get("title", "")),
                description=str(oq.get("description", "")),
                mission=oq.get("mission"),
                status=str(oq.get("status", "open")),
                created_at=parse_dt(oq.get("created_at")),
                resolved_at=parse_optional_dt(oq.get("resolved_at"))
            ))

        # 11. Parse Blockers
        blockers = []
        for b in data.get("blockers", []) or []:
            blockers.append(BlockerEntry(
                id=str(b.get("id", "")),
                description=str(b.get("description", "")),
                created_at=parse_dt(b.get("created_at"))
            ))

        # 12. Parse Recommendations
        recommendations = []
        for r in data.get("recommendations", []) or []:
            recommendations.append(RecommendationEntry(
                id=str(r.get("id", "")),
                suggestion=str(r.get("suggestion", "")),
                proposed_at=parse_dt(r.get("proposed_at"))
            ))

        return EngineeringState(
            project=project,
            workspace=workspace,
            mission=mission,
            provider=provider,
            session=session,
            knowledge_state=knowledge_state,
            decision_state=decision_state,
            timeline_state=timeline_state,
            open_questions=open_questions,
            blockers=blockers,
            recommendations=recommendations,
            version=version
        )

    @classmethod
    def to_dict(cls, state: EngineeringState) -> Dict[str, Any]:
        """Serializes an EngineeringState domain model into a standard Python dictionary structure."""
        return {
            "version": state.version,
            "project": {
                "id": state.project.id,
                "name": state.project.name
            },
            "workspace": {
                "version": state.workspace.version,
                "engineering_phase": state.workspace.engineering_phase
            },
            "mission": {
                "current_mission": state.mission.current_mission,
                "completed_missions": state.mission.completed_missions,
                "mission_history": state.mission.mission_history
            },
            "provider": {
                "current_provider": state.provider.current_provider,
                "provider_history": [
                    {
                        "provider": p.provider,
                        "mission": p.mission,
                        "started_at": p.started_at.isoformat(),
                        "finished_at": p.finished_at.isoformat() if p.finished_at else None
                    } for p in state.provider.provider_history
                ]
            },
            "session": {
                "current_session_id": state.session.current_session_id,
                "latest_session_id": state.session.latest_session_id
            },
            "knowledge_state": {
                "knowledge": [
                    {
                        "id": k.id,
                        "title": k.title,
                        "reference_path": k.reference_path,
                        "category": k.category,
                        "extracted_at": k.extracted_at.isoformat()
                    } for k in state.knowledge_state.knowledge
                ]
            },
            "decision_state": {
                "decisions": [
                    {
                        "id": d.id,
                        "title": d.title,
                        "rationale": d.rationale,
                        "mission": d.mission,
                        "artifact_reference": d.artifact_reference,
                        "decided_at": d.decided_at.isoformat()
                    } for d in state.decision_state.decisions
                ]
            },
            "timeline_state": {
                "event_log": [
                    {
                        "id": ev.id,
                        "event_type": ev.event_type,
                        "description": ev.description,
                        "timestamp": ev.timestamp.isoformat()
                    } for ev in state.timeline_state.event_log
                ]
            },
            "open_questions": [
                {
                    "id": oq.id,
                    "title": oq.title,
                    "description": oq.description,
                    "mission": oq.mission,
                    "status": oq.status,
                    "created_at": oq.created_at.isoformat(),
                    "resolved_at": oq.resolved_at.isoformat() if oq.resolved_at else None
                } for oq in state.open_questions
            ],
            "blockers": [
                {
                    "id": b.id,
                    "description": b.description,
                    "created_at": b.created_at.isoformat()
                } for b in state.blockers
            ],
            "recommendations": [
                {
                    "id": r.id,
                    "suggestion": r.suggestion,
                    "proposed_at": r.proposed_at.isoformat()
                } for r in state.recommendations
            ]
        }
