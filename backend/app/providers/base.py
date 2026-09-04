"""
Abstract LLM Provider Interface.
Defines unified contracts for generation, streaming, and health checks across Local and Cloud models.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List


class LLMProviderInterface(ABC):
    """Unified interface for LLM inference providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical provider identifier (e.g. 'ollama', 'anthropic', 'openai')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the active model name."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs: Any,
    ) -> str:
        """Generates a complete response for the given conversation messages."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Streams text tokens asynchronously for the given conversation messages."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Checks provider reachability and returns health diagnostics."""
        pass
