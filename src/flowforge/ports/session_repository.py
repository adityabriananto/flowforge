from abc import ABC, abstractmethod
from flowforge.domain.engineering_session import EngineeringSession

class EngineeringSessionRepository(ABC):
    @abstractmethod
    def load(self, session_id: str, base_path: str = ".") -> EngineeringSession:
        """Loads an EngineeringSession from persistent storage."""
        pass

    @abstractmethod
    def save(self, session: EngineeringSession, base_path: str = ".") -> None:
        """Saves an EngineeringSession to persistent storage."""
        pass
