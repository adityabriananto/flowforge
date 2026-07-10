from abc import ABC, abstractmethod
from flowforge.domain.engineering_state import EngineeringState

class EngineeringStateRepository(ABC):
    @abstractmethod
    def load(self, base_path: str = ".") -> EngineeringState:
        """Loads the EngineeringState from persistent storage."""
        pass

    @abstractmethod
    def save(self, state: EngineeringState, base_path: str = ".") -> None:
        """Saves the EngineeringState to persistent storage."""
        pass
