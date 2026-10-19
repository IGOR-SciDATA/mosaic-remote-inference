from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=24000)


class InferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[Message] = Field(min_length=1, max_length=200)
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    temperature: float | None = Field(default=None, ge=0, le=2)


class InferenceResponse(BaseModel):
    model: str
    output_text: str


class CapabilitiesResponse(BaseModel):
    service: str
    protocol_version: str
    streaming: bool
    tools: bool
    configured_model: str
