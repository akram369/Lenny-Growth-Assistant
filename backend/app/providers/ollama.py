"""
Ollama Local LLM Provider Driver.
Connects to the local Ollama daemon for inference without cloud dependencies.
"""

import json
import time
from typing import Any, AsyncIterator, Dict, List
import httpx

from app.config import settings
from app.logging_config import logger
from app.providers.base import LLMProviderInterface


class OllamaProvider(LLMProviderInterface):
    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_MODEL,
        timeout: int = settings.OLLAMA_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self.model

    def _prepare_messages(self, messages: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        return formatted

    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Streams tokens from Ollama /api/chat endpoint."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": self._prepare_messages(messages, system_prompt),
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Ollama error ({response.status_code}): {err_text.decode('utf-8', errors='ignore')}")
                        yield f"\n\n[Ollama Error {response.status_code}: Model '{self.model}' may not be pulled. Run `ollama pull {self.model}`.]"
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                yield chunk
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            logger.error(f"Could not connect to Ollama at {self.base_url}")
            yield f"\n\n[Local Inference Error: Cannot connect to Ollama at {self.base_url}. Please ensure Ollama is running (`ollama serve`).]"
        except httpx.TimeoutException:
            logger.error(f"Ollama timed out after {self.timeout}s")
            yield "\n\n[Local Inference Error: Ollama inference timed out.]"
        except Exception as e:
            logger.error(f"Unexpected error in Ollama stream: {e}")
            yield f"\n\n[Local Inference Error: {str(e)}]"

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
        """Probes Ollama daemon and checks if configured model exists."""
        start_time = time.perf_counter()
        try:
            timeout_cfg = httpx.Timeout(2.0, connect=0.5)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                # Check version
                v_res = await client.get(f"{self.base_url}/api/version")
                # Check tags (models)
                t_res = await client.get(f"{self.base_url}/api/tags")

                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                if v_res.status_code == 200 and t_res.status_code == 200:
                    models_data = t_res.json().get("models", [])
                    available_models = [m.get("name") for m in models_data]
                    model_ready = any(self.model in m for m in available_models)

                    return {
                        "status": "healthy",
                        "provider": "ollama",
                        "model": self.model,
                        "model_ready": model_ready,
                        "available_models": available_models,
                        "latency_ms": latency_ms,
                        "endpoint": self.base_url,
                    }
                return {
                    "status": "degraded",
                    "provider": "ollama",
                    "error": f"Unexpected status: {v_res.status_code}",
                    "latency_ms": latency_ms,
                }
        except Exception as e:
            return {
                "status": "offline",
                "provider": "ollama",
                "error": str(e),
                "endpoint": self.base_url,
            }
