from abc import ABC, abstractmethod
from typing import Dict, Any

class ExecutionProvider(ABC):
    @abstractmethod
    async def execute(self, prompt: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the AI task (via CLI process, API request, or local model).
        Returns a structured dictionary mapping:
        {
            "status": "SUCCESS" | "NO_CHANGE" | "FAILED",
            "artifacts": ["path/to/output_file"],
            "metrics": {
                "duration_seconds": float,
                "tokens_used": int
            }
        }
        """
        pass
