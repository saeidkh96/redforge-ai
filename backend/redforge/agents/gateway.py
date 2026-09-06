from __future__ import annotations

import json
from typing import Protocol
from urllib import request

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class LLMProvider(Protocol):
    def complete(self, messages: list[LLMMessage]) -> LLMResponse: ...


class OpenAICompatibleProvider:
    def __init__(
        self, base_url: str, model: str, api_key: str | None = None, timeout: int = 60
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        payload = json.dumps(
            {"model": self.model, "messages": [message.model_dump() for message in messages]}
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(
            content=content,
            model=data.get("model", self.model),
            metadata={"provider": "openai-compatible"},
        )


class StaticProvider:
    """Deterministic provider used by tests and offline development."""

    def __init__(self, content: str) -> None:
        self.content = content

    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        return LLMResponse(
            content=self.content, model="static", metadata={"message_count": len(messages)}
        )
