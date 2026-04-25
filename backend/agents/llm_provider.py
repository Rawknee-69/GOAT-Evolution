from __future__ import annotations

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any

from pydantic import ValidationError

from backend.core.models import BlueAction, RedAction


class LLMProvider(ABC):
    def __init__(self, model: str, temperature: float = 0.2, timeout: float = 10.0):
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    @abstractmethod
    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        raise NotImplementedError


class HuggingFaceProvider(LLMProvider):
    def __init__(self, model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"):
        super().__init__(model)
        from huggingface_hub import AsyncInferenceClient

        self.client = AsyncInferenceClient(provider="auto", token=os.getenv("HF_TOKEN"))

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=self.temperature,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)


class NvidiaNimProvider(LLMProvider):
    def __init__(self, model: str = "meta/llama-3.1-405b-instruct"):
        super().__init__(model)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=self.temperature,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content or "{}")


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=self.temperature,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content or "{}")


class GeminiProvider(LLMProvider):
    def __init__(self, model: str = "gemini-1.5-flash"):
        super().__init__(model)
        from google.generativeai import GenerativeModel

        self.model_client = GenerativeModel(model)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        prompt = f"{system_prompt}\n\n{user_prompt}\nRespond in JSON only."
        resp = await self.model_client.generate_content_async(prompt)
        return json.loads(resp.text)


class ScriptedProvider(LLMProvider):
    def __init__(self):
        super().__init__(model="scripted")

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {}


def parse_with_retry(payload: dict[str, Any], role: str, retries: int = 2) -> RedAction | BlueAction:
    last_err: Exception | None = None
    model = RedAction if role == "red" else BlueAction
    for _ in range(retries + 1):
        try:
            return model.model_validate(payload)
        except ValidationError as exc:
            last_err = exc
    raise last_err or ValueError("invalid payload")
