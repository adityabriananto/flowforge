from abc import ABC, abstractmethod
from typing import Dict, Any
from flowforge.domain.mission_package import MissionPackage

class AIProvider(ABC):
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name of the AI provider."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Returns deterministic provider health status info."""
        pass

    @abstractmethod
    def execute(self, mission_package: MissionPackage, **kwargs) -> Dict[str, Any]:
        """Executes the engineering tasks described in the MissionPackage."""
        pass
