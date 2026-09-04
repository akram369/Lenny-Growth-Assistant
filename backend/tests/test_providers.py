"""
Unit Tests for LLM Providers and Dynamic Routing Factory.
"""

import pytest
from app.providers.factory import get_provider, get_all_providers_status
from app.providers.ollama import OllamaProvider
from app.providers.cloud import CloudProvider


@pytest.mark.asyncio
async def test_provider_factory_resolution():
    ollama = get_provider("ollama")
    assert isinstance(ollama, OllamaProvider)
    assert ollama.provider_name == "ollama"

    cloud = get_provider("cloud")
    assert isinstance(cloud, CloudProvider)
    assert "cloud" in cloud.provider_name

    openai = get_provider("openai")
    assert isinstance(openai, CloudProvider)
    assert openai.driver == "openai"


@pytest.mark.asyncio
async def test_provider_health_checks():
    providers_status = await get_all_providers_status()
    assert len(providers_status) >= 2
    assert any(p["id"] == "ollama" for p in providers_status)
    assert any(p["id"] == "cloud" for p in providers_status)


@pytest.mark.asyncio
async def test_cloud_provider_missing_key():
    # If no API key is provided, cloud provider should yield a clean diagnostic message rather than crashing
    cloud = CloudProvider(driver="anthropic")
    cloud.api_key = ""

    messages = [{"role": "user", "content": "Hello"}]
    tokens = []
    async for token in cloud.stream(messages):
        tokens.append(token)

    response = "".join(tokens)
    assert "Configuration Notice" in response or "No API key" in response
