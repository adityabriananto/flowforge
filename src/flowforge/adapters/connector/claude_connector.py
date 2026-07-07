import os
from typing import Optional
import httpx
from flowforge.ports.connector import ExecutionConnector

class ClaudeConnector(ExecutionConnector):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.api_url = "https://api.anthropic.com/v1/messages"

        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set via ANTHROPIC_API_KEY env variable.")

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        if system_instruction:
            payload["system"] = system_instruction

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                # Mask API Key in error log to ensure safety
                masked_key = self.api_key[:6] + "..." + self.api_key[-4:] if len(self.api_key) > 10 else "***"
                raise RuntimeError(
                    f"Anthropic API request failed with status {response.status_code}. "
                    f"Response: {response.text}. API Key used: {masked_key}"
                )
                
            data = response.json()
            # Extract content from response structure
            content_list = data.get("content", [])
            if content_list and content_list[0].get("type") == "text":
                return content_list[0].get("text", "")
            return ""
