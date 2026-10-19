import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app


class FakeAdapter:
    def set_configured_model(self, model):
        self.model = model

    async def ready(self):
        return True

    async def generate(self, **kwargs):
        return "Resposta de teste"


@pytest.fixture
def client():
    settings = Settings(api_token="test-secret-token", runtime_model="test-model", max_input_chars=100, max_messages=3)
    from app.services.inference_service import InferenceService
    service = InferenceService(settings, adapter=FakeAdapter())
    with TestClient(create_app(settings, service)) as test_client:
        yield test_client
