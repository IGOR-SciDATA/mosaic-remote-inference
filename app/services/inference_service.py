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

    async def infer(self, request: InferenceRequest) -> str:
        if len(request.messages) > self.settings.max_messages:
            raise ValueError("Request exceeds configured message limit")
        total_chars = sum(len(message.content) for message in request.messages)
        if total_chars > self.settings.max_input_chars:
            raise ValueError("Request exceeds configured input limit")
        return await self.adapter.generate(
            model=self.settings.runtime_model,
            messages=[message.model_dump() for message in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
