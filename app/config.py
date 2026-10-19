"""Environment-based configuration for the standalone inference service."""
from dataclasses import dataclass
import os
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    api_token: str
    runtime_base_url: str = "http://127.0.0.1:11434"
    runtime_model: str = "qwen2.5:3b"
    request_timeout_seconds: float = 90.0
    max_input_chars: int = 24000
    max_messages: int = 40
    service_name: str = "mosaic-remote-inference"

    @classmethod
    def from_env(cls) -> "Settings":
        runtime_url = os.getenv("MOSAIC_RUNTIME_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        parsed = urlsplit(runtime_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Invalid configuration: MOSAIC_RUNTIME_BASE_URL")
        return cls(
            api_token=os.getenv("MOSAIC_REMOTE_INFERENCE_TOKEN", ""),
            runtime_base_url=runtime_url,
            runtime_model=os.getenv("MOSAIC_RUNTIME_MODEL", "qwen2.5:3b"),
            request_timeout_seconds=_bounded_float("MOSAIC_INFERENCE_TIMEOUT_SECONDS", 90.0, 1.0, 600.0),
            max_input_chars=_bounded_int("MOSAIC_MAX_INPUT_CHARS", 24000, 1, 100000),
            max_messages=_bounded_int("MOSAIC_MAX_MESSAGES", 40, 1, 200),
        )


def _bounded_float(name: str, default: float, low: float, high: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"Invalid configuration: {name}") from exc
    if not low <= value <= high:
        raise ValueError(f"Invalid configuration: {name}")
    return value


def _bounded_int(name: str, default: int, low: int, high: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"Invalid configuration: {name}") from exc
    if not low <= value <= high:
        raise ValueError(f"Invalid configuration: {name}")
    return value
