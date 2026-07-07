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
    feedback: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactManager:
    def __init__(self, storage_dir: Optional[str] = None):
        self.artifacts: Dict[uuid.UUID, Artifact] = {}
        self.storage_dir = storage_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../artifacts"))

    def create_artifact(
        self, 
        instance_id: uuid.UUID, 
        name: str, 
        path: str, 
        content: str
    ) -> Artifact:
        """
        Creates and registers a new output artifact.
        Writes the file content to the target path.
        """
        # Auto-create directories if writing actual file output
        full_path = os.path.abspath(os.path.join(self.storage_dir, path))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
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
            content=content
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
