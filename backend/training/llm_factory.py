"""Factory for selecting LLM providers + agents at trainer startup.

Centralizes provider construction so the CLI can pass simple strings like
"gemini" / "openai" / "huggingface" / "scripted" and we get back the right
agent/judge instances. Falls back to the scripted agents when a provider is
unavailable so the loop never silently breaks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from backend.agents.blue_agent import BlueAgent
from backend.agents.llm_provider import (
    GeminiProvider,
    HuggingFaceProvider,
    LLMProvider,
    NvidiaNimProvider,
    OpenAIProvider,
    ScriptedProvider,
)
from backend.agents.red_agent import RedAgent
from backend.agents.scripted import ScriptedBlueAgent, ScriptedRedAgent
from backend.training.llm_judge import LLMJudge


PROVIDER_KEYS = {"gemini", "openai", "huggingface", "nvidia", "scripted"}


def build_provider(name: str, model: str | None = None) -> LLMProvider | None:
    """Construct a provider; return None if env is missing the required key."""
    name = name.lower().strip()
    if name == "scripted":
        return ScriptedProvider()
    try:
        if name == "gemini":
            if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
                return None
            return GeminiProvider(model=model or "gemini-2.5-flash")
        if name == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                return None
            return OpenAIProvider(model=model or "gpt-4o-mini")
        if name == "huggingface":
            if not os.getenv("HF_TOKEN"):
                return None
            return HuggingFaceProvider(
                model=model or "meta-llama/Meta-Llama-3.1-8B-Instruct"
            )
        if name == "nvidia":
            if not os.getenv("NVIDIA_API_KEY"):
                return None
            return NvidiaNimProvider(model=model or "meta/llama-3.1-405b-instruct")
    except Exception:
        return None
    return None


@dataclass
class AgentTrio:
    red: Any
    blue: Any
    judge: LLMJudge | None
    red_kind: str
    blue_kind: str
    judge_kind: str
    red_provider_name: str
    blue_provider_name: str
    judge_provider_name: str


def build_agents(
    *,
    red_provider_name: str,
    blue_provider_name: str,
    judge_provider_name: str,
    red_model: str | None = None,
    blue_model: str | None = None,
    judge_model: str | None = None,
) -> AgentTrio:
    red_provider = build_provider(red_provider_name, model=red_model)
    blue_provider = build_provider(blue_provider_name, model=blue_model)
    judge_provider = build_provider(judge_provider_name, model=judge_model)

    if red_provider and not isinstance(red_provider, ScriptedProvider):
        red_agent: Any = RedAgent(provider=red_provider)
        red_kind = "llm"
    else:
        red_agent = ScriptedRedAgent()
        red_kind = "scripted"

    if blue_provider and not isinstance(blue_provider, ScriptedProvider):
        blue_agent: Any = BlueAgent(provider=blue_provider)
        blue_kind = "llm"
    else:
        blue_agent = ScriptedBlueAgent()
        blue_kind = "scripted"

    if judge_provider and not isinstance(judge_provider, ScriptedProvider):
        judge: LLMJudge | None = LLMJudge(provider=judge_provider)
        judge_kind = "llm"
    else:
        judge = None
        judge_kind = "scripted"

    return AgentTrio(
        red=red_agent,
        blue=blue_agent,
        judge=judge,
        red_kind=red_kind,
        blue_kind=blue_kind,
        judge_kind=judge_kind,
        red_provider_name=red_provider_name,
        blue_provider_name=blue_provider_name,
        judge_provider_name=judge_provider_name,
    )
