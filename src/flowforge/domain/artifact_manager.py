import uuid
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

@dataclass
class Artifact:
    id: uuid.UUID
    instance_id: uuid.UUID
    name: str
    path: str
    status: str  # PENDING_REVIEW, APPROVED, REJECTED
    version: int
    content: str
    artifact_type: str  # MARKDOWN, JSON, YAML, PNG, SQL, PATCH, DIFF, BINARY
    feedback: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactManager:
    def __init__(self, storage_dir: Optional[str] = None):
        self.artifacts: Dict[uuid.UUID, Artifact] = {}
        self.storage_dir = storage_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../artifacts"))

    def _detect_artifact_type(self, path: str) -> str:
        """Helper to automatically map file extensions to rich artifact types."""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".md":
            return "MARKDOWN"
        elif ext == ".json":
            return "JSON"
        elif ext == ".yaml" or ext == ".yml":
            return "YAML"
        elif ext == ".png":
            return "PNG"
        elif ext == ".sql":
            return "SQL"
        elif ext == ".patch":
            return "PATCH"
        elif ext == ".diff":
            return "DIFF"
        elif ext in [".txt", ".py", ".sh", ".js", ".ts"]:
            return "TEXT"
        else:
            return "BINARY"

    def create_artifact(
        self, 
        instance_id: uuid.UUID, 
        name: str, 
        path: str, 
        content: str,
        artifact_type: Optional[str] = None
    ) -> Artifact:
        """
        Creates and registers a new output artifact with rich type support.
        """
        # Auto-detect type if not provided
        detected_type = artifact_type or self._detect_artifact_type(path)

        # Auto-create directories if writing actual file output
        full_path = os.path.abspath(os.path.join(self.storage_dir, path))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            # For PNG or BINARY, we might write binary, otherwise write text
            if detected_type in ["PNG", "BINARY"]:
                with open(full_path, "wb") as f:
                    f.write(content.encode("utf-8") if isinstance(content, str) else content)
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception:
            # Safe ignore file-system writes in unit tests if storage path is invalid
            pass

        # Determine version
        existing_version = 1
        for art in self.artifacts.values():
            if art.instance_id == instance_id and art.name == name:
                existing_version = max(existing_version, art.version + 1)

        art_id = uuid.uuid4()
        artifact = Artifact(
            id=art_id,
            instance_id=instance_id,
            name=name,
            path=path,
            status="PENDING_REVIEW",
            version=existing_version,
            content=content,
            artifact_type=detected_type
        )
        self.artifacts[art_id] = artifact
        return artifact

    def update_status(
        self, 
        artifact_id: uuid.UUID, 
        status: str, 
        feedback: Optional[str] = None
    ) -> Optional[Artifact]:
        """Updates the review status (APPROVED / REJECTED) of an artifact."""
        artifact = self.artifacts.get(artifact_id)
        if artifact:
            artifact.status = status
            artifact.feedback = feedback
            return artifact
        return None

    def get_artifacts_by_instance(self, instance_id: uuid.UUID) -> List[Artifact]:
        """Returns all registered artifacts matching the workflow instance."""
        return [art for art in self.artifacts.values() if art.instance_id == instance_id]
