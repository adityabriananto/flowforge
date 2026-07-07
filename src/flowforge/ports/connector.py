from abc import ABC, abstractmethod
from typing import Optional

class ExecutionConnector(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Sends a request to an Execution Connector and returns the text response.
        The connector may be an AI model, a system tool, a human proxy, or any other execution backend.
        """
        pass
