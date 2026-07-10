import yaml
from datetime import datetime
from typing import Dict, Any
from flowforge.domain.engineering_state import (
    EngineeringState,
    ProjectState,
    WorkspaceState,
    MissionStateInfo,
    ProviderStateInfo,
    SessionStateInfo,
    KnowledgeEntry,
    DecisionEntry,
    BlockerEntry,
    RecommendationEntry,
    MilestoneEntry
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
        mission = MissionStateInfo(
            current_mission=m_data.get("current_mission"),
            completed_missions=list(m_data.get("completed_missions", [])),
            mission_history=list(m_data.get("mission_history", []))
        )

        # 5. Parse Provider State
        p_data = data.get("provider", {})
        provider = ProviderStateInfo(
            current_provider=p_data.get("current_provider"),
            provider_history=list(p_data.get("provider_history", []))
        )

        # 6. Parse Session State
        s_data = data.get("session", {})
        session = SessionStateInfo(
            current_session_id=s_data.get("current_session_id"),
            latest_session_id=s_data.get("latest_session_id")
        )

        # Helper to parse datetime safely
        def parse_dt(dt_str: Any) -> datetime:
            if not dt_str:
                return datetime.utcnow()
            try:
                return datetime.fromisoformat(str(dt_str))
            except ValueError:
                return datetime.utcnow()

        # 7. Parse Knowledge
        knowledge = []
        for k in data.get("knowledge", []) or []:
            knowledge.append(KnowledgeEntry(
                id=str(k.get("id", "")),
                title=str(k.get("title", "")),
                reference_path=str(k.get("reference_path", "")),
                extracted_at=parse_dt(k.get("extracted_at"))
            ))

        # 8. Parse Decisions
        decisions = []
        for d in data.get("decisions", []) or []:
            decisions.append(DecisionEntry(
                id=str(d.get("id", "")),
                title=str(d.get("title", "")),
                rationale=str(d.get("rationale", "")),
                decided_at=parse_dt(d.get("decided_at"))
            ))

        # 9. Parse Open Questions
        open_questions = list(data.get("open_questions", []) or [])

        # 10. Parse Blockers
        blockers = []
        for b in data.get("blockers", []) or []:
            blockers.append(BlockerEntry(
                id=str(b.get("id", "")),
                description=str(b.get("description", "")),
                created_at=parse_dt(b.get("created_at"))
            ))

        # 11. Parse Recommendations
        recommendations = []
        for r in data.get("recommendations", []) or []:
            recommendations.append(RecommendationEntry(
                id=str(r.get("id", "")),
                suggestion=str(r.get("suggestion", "")),
                proposed_at=parse_dt(r.get("proposed_at"))
            ))

        # 12. Parse Timeline
        timeline = []
        for t in data.get("timeline", []) or []:
            timeline.append(MilestoneEntry(
                id=str(t.get("id", "")),
                title=str(t.get("title", "")),
                target_date=t.get("target_date")
            ))

        return EngineeringState(
            project=project,
            workspace=workspace,
            mission=mission,
            provider=provider,
            session=session,
            knowledge=knowledge,
            decisions=decisions,
            open_questions=open_questions,
            blockers=blockers,
            recommendations=recommendations,
            timeline=timeline,
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
                "provider_history": state.provider.provider_history
            },
            "session": {
                "current_session_id": state.session.current_session_id,
                "latest_session_id": state.session.latest_session_id
            },
            "knowledge": [
                {
                    "id": k.id,
                    "title": k.title,
                    "reference_path": k.reference_path,
                    "extracted_at": k.extracted_at.isoformat()
                } for k in state.knowledge
            ],
            "decisions": [
                {
                    "id": d.id,
                    "title": d.title,
                    "rationale": d.rationale,
                    "decided_at": d.decided_at.isoformat()
                } for d in state.decisions
            ],
            "open_questions": state.open_questions,
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
            ],
            "timeline": [
                {
                    "id": t.id,
                    "title": t.title,
                    "target_date": t.target_date
                } for t in state.timeline
            ]
        }
