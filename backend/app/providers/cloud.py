"""
Cloud LLM Provider Driver (Anthropic Claude & OpenAI).
Enables seamless switching to cloud models for advanced synthesis and complex artifact generation.
"""

from typing import Any, AsyncIterator, Dict, List
import httpx

from app.config import settings
from app.logging_config import logger
from app.providers.base import LLMProviderInterface


class CloudProvider(LLMProviderInterface):
    def __init__(
        self,
        driver: str = settings.CLOUD_PROVIDER,  # "anthropic" or "openai"
    ):
        self.driver = driver.lower()
        if self.driver == "anthropic":
            self.api_key = settings.ANTHROPIC_API_KEY
            self.model = settings.ANTHROPIC_MODEL
        else:
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL

    @property
    def provider_name(self) -> str:
        return f"cloud-{self.driver}"

    @property
    def model_name(self) -> str:
        return self.model

    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Streams tokens from Cloud provider (Anthropic or OpenAI)."""
        if not self.api_key:
            yield f"\n\n[Configuration Notice: No API key configured for {self.driver.capitalize()}. Please set {self.driver.upper()}_API_KEY in .env or switch to Local LLM (Ollama).]"
            return

        if self.driver == "anthropic":
            async for token in self._stream_anthropic(messages, system_prompt, **kwargs):
                yield token
        else:
            async for token in self._stream_openai(messages, system_prompt, **kwargs):
                yield token

    async def _stream_anthropic(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            formatted = [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in messages
                if m.get("role") in ("user", "assistant")
            ]

            async with client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4096),
                system=system_prompt,
                messages=formatted,
                temperature=kwargs.get("temperature", 0.3),
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic API stream error: {e}")
            yield f"\n\n[Anthropic API Error: {str(e)}]"

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            formatted = []
            if system_prompt:
                formatted.append({"role": "system", "content": system_prompt})
            for m in messages:
                formatted.append({"role": m.get("role", "user"), "content": m.get("content", "")})

            response = await client.chat.completions.create(
                model=self.model,
                messages=formatted,
                stream=True,
                temperature=kwargs.get("temperature", 0.3),
            )
            async for chunk in response:
                delta = chunk.choices[0].delta.content if chunk.choices else ""
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"OpenAI API stream error: {e}")
            yield f"\n\n[OpenAI API Error: {str(e)}]"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs: Any,
    ) -> str:
        tokens = []
        async for token in self.stream(messages, system_prompt, **kwargs):
            tokens.append(token)
        return "".join(tokens)

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and len(self.api_key) > 5)
        return {
            "status": "ready" if has_key else "unconfigured",
            "provider": self.provider_name,
            "driver": self.driver,
            "model": self.model,
            "configured": has_key,
        }
