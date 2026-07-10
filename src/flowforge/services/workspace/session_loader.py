import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List
from flowforge.domain.engineering_session import (
    EngineeringSession,
    SessionMetadata,
    SessionStatus
)

class EngineeringSessionLoader:
    @classmethod
    def load_from_yaml(cls, yaml_content: str) -> EngineeringSession:
        """Parses YAML content and constructs a validated EngineeringSession domain model."""
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")

        if not data:
            raise ValueError("Empty or invalid EngineeringSession YAML content")

        # 1. Version Validation
        version = str(data.get("version", "1"))
        if version != "1":
            raise ValueError(f"Unsupported EngineeringSession version '{version}'. Only version '1' is supported.")

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

        # 2. Parse Metadata
        meta_data = data.get("metadata", {})
        metadata = SessionMetadata(
            session_id=str(meta_data.get("session_id", "")),
            provider=str(meta_data.get("provider", "Unknown")),
            mission=str(meta_data.get("mission", "Unknown")),
            started_at=parse_dt(meta_data.get("started_at")),
            finished_at=parse_optional_dt(meta_data.get("finished_at")),
            duration_seconds=meta_data.get("duration_seconds"),
            status=SessionStatus(meta_data.get("status", "CREATED"))
        )

        return EngineeringSession(
            metadata=metadata,
            summary=data.get("summary"),
            artifacts=list(data.get("artifacts", []) or []),
            decisions=list(data.get("decisions", []) or []),
            files_changed=list(data.get("files_changed", []) or []),
            warnings=list(data.get("warnings", []) or []),
            open_questions=list(data.get("open_questions", []) or []),
            blockers=list(data.get("blockers", []) or []),
            recommendations=list(data.get("recommendations", []) or []),
            handover_summary=data.get("handover_summary"),
            version=version
        )

    @classmethod
    def to_dict(cls, session: EngineeringSession) -> Dict[str, Any]:
        """Serializes an EngineeringSession domain model into a standard Python dictionary structure."""
        return {
            "version": session.version,
            "metadata": {
                "session_id": session.metadata.session_id,
                "provider": session.metadata.provider,
                "mission": session.metadata.mission,
                "started_at": session.metadata.started_at.isoformat(),
                "finished_at": session.metadata.finished_at.isoformat() if session.metadata.finished_at else None,
                "duration_seconds": session.metadata.duration_seconds,
                "status": session.metadata.status.value
            },
            "summary": session.summary,
            "artifacts": session.artifacts,
            "decisions": session.decisions,
            "files_changed": session.files_changed,
            "warnings": session.warnings,
            "open_questions": session.open_questions,
            "blockers": session.blockers,
            "recommendations": session.recommendations,
            "handover_summary": session.handover_summary
        }
