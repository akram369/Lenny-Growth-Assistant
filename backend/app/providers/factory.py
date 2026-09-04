"""
Dynamic LLM Provider Factory and Router.
Resolves and instantiates the active LLM provider based on request headers, parameters, or defaults.
"""

from typing import Any, Dict, List, Optional
from app.config import settings
from app.providers.base import LLMProviderInterface
from app.providers.ollama import OllamaProvider
from app.providers.cloud import CloudProvider
from app.logging_config import logger


_ollama_instance = None
_cloud_instance = None


def get_provider(provider_name: Optional[str] = None) -> LLMProviderInterface:
    """
    Returns the appropriate LLMProviderInterface instance based on requested provider or defaults.
    Supported identifiers: 'ollama', 'cloud', 'anthropic', 'openai'.
    """
    global _ollama_instance, _cloud_instance
    target = (provider_name or settings.DEFAULT_LLM_PROVIDER).lower().strip()

    if target in ("cloud", "anthropic", "openai"):
        driver = "openai" if target == "openai" else "anthropic"
        if _cloud_instance is None or _cloud_instance.driver != driver:
            _cloud_instance = CloudProvider(driver=driver)
        return _cloud_instance

    # Default to Ollama (mandatory for local evaluation)
    if _ollama_instance is None:
        _ollama_instance = OllamaProvider()
    return _ollama_instance


async def get_all_providers_status() -> List[Dict[str, Any]]:
    """Returns health and status of all configured providers for frontend display."""
    ollama = get_provider("ollama")
    cloud = get_provider("cloud")

    ollama_health = await ollama.health_check()
    cloud_health = await cloud.health_check()

    return [
        {
            "id": "ollama",
            "name": "Local LLM (Ollama)",
            "is_default": settings.DEFAULT_LLM_PROVIDER == "ollama",
            **ollama_health,
        },
        {
            "id": "cloud",
            "name": f"Cloud LLM ({cloud.provider_name})",
            "is_default": settings.DEFAULT_LLM_PROVIDER == "cloud",
            **cloud_health,
        },
    ]
