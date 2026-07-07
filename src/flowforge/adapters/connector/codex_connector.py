import os
from typing import Optional
import httpx
from flowforge.ports.connector import LlmConnector

class CodexConnector(LlmConnector):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.api_url = "https://api.openai.com/v1/chat/completions"

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set via OPENAI_API_KEY env variable.")

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

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
                    f"OpenAI API request failed with status {response.status_code}. "
                    f"Response: {response.text}. API Key used: {masked_key}"
                )

            data = response.json()
            choices = data.get("choices", [])
            if choices and choices[0].get("message"):
                return choices[0]["message"].get("content", "")
            return ""
