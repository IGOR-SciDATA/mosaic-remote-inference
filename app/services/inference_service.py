from collections.abc import AsyncIterator

from app.adapters.ollama import OllamaAdapter
from app.config import Settings
from app.schemas import InferenceRequest


class InferenceService:
    def __init__(self, settings: Settings, adapter: OllamaAdapter | None = None):
        self.settings = settings
        self.adapter = adapter or OllamaAdapter(settings.runtime_base_url, settings.request_timeout_seconds)
        self.adapter.set_configured_model(settings.runtime_model)

    async def ready(self) -> bool:
        return await self.adapter.ready()

    def _validate(self, request: InferenceRequest) -> list[dict]:
        if len(request.messages) > self.settings.max_messages:
            raise ValueError("Request exceeds configured message limit")
        total_chars = sum(len(message.content) for message in request.messages)
        if total_chars > self.settings.max_input_chars:
            raise ValueError("Request exceeds configured input limit")
        return [message.model_dump() for message in request.messages]

    async def infer(self, request: InferenceRequest) -> str:
        messages = self._validate(request)
        return await self.adapter.generate(
            model=self.settings.runtime_model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

    async def stream(self, request: InferenceRequest) -> AsyncIterator[str]:
        messages = self._validate(request)
        async for chunk in self.adapter.stream(
            model=self.settings.runtime_model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        ):
            if chunk:
                yield chunk
