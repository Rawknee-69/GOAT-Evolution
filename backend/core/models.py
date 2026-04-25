from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class AttackComponent(str, Enum):
    CRESCENDO = "crescendo"
    DETAIL_ESCALATION = "detail_escalation"
    PERSONA_SHIFT = "persona_shift"
    HYPOTHETICAL_FRAME = "hypothetical_frame"
    CHAINED_REASONING = "chained_reasoning"


class DefenseComponent(str, Enum):
    EARLY_INTERVENTION = "early_intervention"
    PATTERN_FLAG = "pattern_flag"
    TOPIC_REDIRECT = "topic_redirect"
    SAFE_COMPLETION = "safe_completion"
    EDUCATIONAL_REFUSAL = "educational_refusal"


class ModelProfile(str, Enum):
    STANDARD = "standard"
    CREATIVE = "creative"
    HELPFUL = "helpful"


class RedActionPayload(BaseModel):
    strategy: list[AttackComponent] = Field(default_factory=list)
    thought: str = ""
    predicted_target_response: Literal["comply", "refuse", "partial"] = "partial"


class BlueActionPayload(BaseModel):
    defense: list[DefenseComponent] = Field(default_factory=list)
    threat_level: Literal["low", "medium", "high", "critical"] = "low"
    thought: str = ""


class GOATAction(BaseModel):
    role: Literal["red", "blue"]
    red_payload: RedActionPayload | None = None
    blue_payload: BlueActionPayload | None = None


class ConversationTurn(BaseModel):
    turn_index: int
    red_strategy: list[AttackComponent] = Field(default_factory=list)
    blue_defense: list[DefenseComponent] = Field(default_factory=list)
    target_response: str
    violation_score: float


class GOATObservation(BaseModel):
    session_id: str
    task_id: int
    turn: int
    max_turns: int
    history: list[ConversationTurn] = Field(default_factory=list)
    cumulative_red_reward: float = 0.0
    cumulative_blue_reward: float = 0.0
    done: bool = False


class GOATState(BaseModel):
    session_id: str
    task_id: int
    max_turns: int
    turn: int = 0
    history: list[ConversationTurn] = Field(default_factory=list)
    cumulative_red_reward: float = 0.0
    cumulative_blue_reward: float = 0.0
    done: bool = False


class BattleStartRequest(BaseModel):
    task_id: int = 4
    max_turns: int = 8


class VulnerabilityEntry(BaseModel):
    attack_id: str
    components: list[AttackComponent] = Field(default_factory=list)
    target_model: str = "simulator"
    novelty_score: float = 0.0
    discovered_at: str
