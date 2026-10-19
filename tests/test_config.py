import pytest
from app.config import Settings


def test_rejects_runtime_url_with_unsupported_scheme(monkeypatch):
    monkeypatch.setenv("MOSAIC_RUNTIME_BASE_URL", "file:///etc/passwd")
    with pytest.raises(ValueError, match="MOSAIC_RUNTIME_BASE_URL"):
        Settings.from_env()


def test_rejects_runtime_url_with_embedded_credentials(monkeypatch):
    monkeypatch.setenv("MOSAIC_RUNTIME_BASE_URL", "http://user:password@example.com:11434")
    with pytest.raises(ValueError, match="MOSAIC_RUNTIME_BASE_URL"):
        Settings.from_env()


def test_accepts_http_runtime_url(monkeypatch):
    monkeypatch.setenv("MOSAIC_RUNTIME_BASE_URL", "http://127.0.0.1:11434/")
    settings = Settings.from_env()
    assert settings.runtime_base_url == "http://127.0.0.1:11434"
