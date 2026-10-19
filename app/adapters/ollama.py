"""Minimal non-streaming Ollama runtime adapter. Exceptions are normalized upstream."""
import httpx


class RuntimeUnavailable(Exception):
    pass


class OllamaAdapter:
    def __init__(self, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._configured_model = ""

    async def generate(self, *, model: str, messages: list[dict], max_tokens: int | None, temperature: float | None) -> str:
        options = {}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if temperature is not None:
            options["temperature"] = temperature
        payload = {"model": model, "messages": messages, "stream": False}
        if options:
            payload["options"] = options
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
            content = data.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise RuntimeUnavailable("Runtime returned an empty response")
            return content
        except RuntimeUnavailable:
            raise
        except (httpx.HTTPError, ValueError, TypeError, AttributeError) as exc:
            raise RuntimeUnavailable("Inference runtime unavailable or returned an invalid response") from exc

    async def ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout_seconds, 3.0)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
            models = data.get("models", [])
            return any(item.get("name") == self._configured_model for item in models)
        except Exception:
            return False

    def set_configured_model(self, model: str) -> None:
        self._configured_model = model
