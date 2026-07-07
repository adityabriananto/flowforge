import sys
import os
import pytest
from unittest.mock import patch

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.adapters.connector.claude_connector import ClaudeConnector
from flowforge.adapters.connector.codex_connector import CodexConnector

@pytest.mark.asyncio
async def test_missing_api_keys():
    # Remove env variable mockingly to verify ValueError
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            ClaudeConnector()
        assert "Anthropic API key" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            CodexConnector()
        assert "OpenAI API key" in str(exc_info.value)

@pytest.mark.asyncio
async def test_claude_connector_success(httpx_mock):
    # Setup mock response for Anthropic API call
    httpx_mock.add_response(
        url="https://api.anthropic.com/v1/messages",
        status_code=200,
        json={
            "content": [
                {"type": "text", "text": "Hello, this is Claude response!"}
            ]
        }
    )

    connector = ClaudeConnector(api_key="sk-ant-test-key-1234567890", model="claude-3-5-sonnet")
    response = await connector.generate_text(
        prompt="Hi Claude",
        system_instruction="You are a helpful coding assistant"
    )

    assert response == "Hello, this is Claude response!"

@pytest.mark.asyncio
async def test_claude_connector_api_error(httpx_mock):
    # Setup mock error response
    httpx_mock.add_response(
        url="https://api.anthropic.com/v1/messages",
        status_code=500,
        text="Internal Server Error"
    )

    connector = ClaudeConnector(api_key="sk-ant-test-key-1234567890", model="claude-3-5-sonnet")
    
    with pytest.raises(RuntimeError) as exc_info:
        await connector.generate_text(prompt="Hi Claude")
    
    assert "Anthropic API request failed with status 500" in str(exc_info.value)
    # Ensure key is masked in error message
    assert "sk-ant...7890" in str(exc_info.value)
    assert "sk-ant-test-key-1234567890" not in str(exc_info.value)

@pytest.mark.asyncio
async def test_codex_connector_success(httpx_mock):
    # Setup mock response for OpenAI API call
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        status_code=200,
        json={
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello, this is OpenAI response!"}
                }
            ]
        }
    )

    connector = CodexConnector(api_key="sk-proj-test-key-1234567890", model="gpt-4o")
    response = await connector.generate_text(
        prompt="Hi Codex",
        system_instruction="You are an expert coder"
    )

    assert response == "Hello, this is OpenAI response!"

@pytest.mark.asyncio
async def test_codex_connector_api_error(httpx_mock):
    # Setup mock error response
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        status_code=401,
        text="Unauthorized Access"
    )

    connector = CodexConnector(api_key="sk-proj-test-key-1234567890", model="gpt-4o")

    with pytest.raises(RuntimeError) as exc_info:
        await connector.generate_text(prompt="Hi Codex")

    assert "OpenAI API request failed with status 401" in str(exc_info.value)
    # Ensure key is masked in error message
    assert "sk-pro...7890" in str(exc_info.value)
    assert "sk-proj-test-key-1234567890" not in str(exc_info.value)
