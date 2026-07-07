from abc import ABC, abstractmethod
from typing import Optional

class LlmConnector(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Sends a request to the LLM Provider and returns the text response.
        """
        pass
