import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from flowforge.domain.mission import Mission, MissionState

class MissionFactory:
    """
    Factory for creating Mission domain objects.
    """
    
    @staticmethod
    def create(
        title: str, 
        description: str, 
        code: str,
        goals: Optional[List[str]] = None, 
        metadata: Optional[Dict[str, Any]] = None,
        priority: str = "medium"
    ) -> Mission:
        return Mission(
            id=uuid.uuid4(),
            title=title,
            description=description,
            status=MissionState.BACKLOG,
            code=code,
            goals=goals or [],
            metadata=metadata or {},
            priority=priority,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
