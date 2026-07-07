import time
from typing import Dict, Any
from flowforge.ports.execution_provider import ExecutionProvider
from flowforge.ports.connector import LlmConnector

class ApiExecutionProvider(ExecutionProvider):
    def __init__(self, connector: LlmConnector):
        self.connector = connector

    async def execute(self, prompt: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Directly execute API call without CLI process (Challenge #10)
            response_text = await self.connector.generate_text(
                prompt=prompt,
                system_instruction=variables.get("system_instruction")
            )
            status = "SUCCESS"
            # Simulate or parse artifacts list from response if needed
            artifacts = variables.get("artifacts", [])
        except Exception:
            response_text = ""
            status = "FAILED"
            artifacts = []
            
        duration = time.time() - start_time
        
        # Estimate tokens (average 4 chars per token)
        tokens = len(prompt + response_text) // 4
        
        return {
            "status": status,
            "artifacts": artifacts,
            "content": response_text,
            "metrics": {
                "duration_seconds": round(duration, 3),
                "tokens_used": tokens
            }
        }
