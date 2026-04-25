from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AttackComponent(str, Enum):
    PERSONA_SHIFT = "persona_shift"
    HYPOTHETICAL_FRAME = "hypothetical_frame"
    REFUSAL_SUPPRESSION = "refusal_suppression"
    DETAIL_ESCALATION = "detail_escalation"
    CRESCENDO = "crescendo"
    CONTEXT_INJECTION = "context_injection"
    AUTHORITY_CLAIM = "authority_claim"
    EMOTIONAL_APPEAL = "emotional_appeal"
    INDIRECT_ELICITATION = "indirect_elicitation"
    TECHNICAL_FRAMING = "technical_framing"


class DefenseComponent(str, Enum):
    FLAT_REFUSE = "flat_refuse"
    TOPIC_REDIRECT = "topic_redirect"
    EARLY_INTERVENTION = "early_intervention"
    CONTEXT_RESET = "context_reset"
    HONEYPOT_RESPONSE = "honeypot_response"
    PATTERN_FLAG = "pattern_flag"
    SOCRATIC_COUNTER = "socratic_counter"
    DELAY_TACTIC = "delay_tactic"


class ModelProfile(str, Enum):
    WEAK = "weak_model"
    STANDARD = "standard_model"
    HARDENED = "hardened_model"


class RedAction(BaseModel):
    operation: Literal["deploy_strategy", "mutate_strategy", "observe", "concede"]
    current_strategy: Optional[list[AttackComponent]] = None
    turn_message: Optional[str] = Field(default=None, max_length=200)
    mutation_reason: str = Field(default="", max_length=300)
    thought: str = Field(default="", max_length=1000)
    predicted_target_response: Literal["comply", "refuse", "partial"] = "refuse"


class BlueAction(BaseModel):
    operation: Literal["deploy_defense", "mutate_defense", "observe", "concede"]
    current_defense: Optional[list[DefenseComponent]] = None
    detected_attack_pattern: Optional[list[AttackComponent]] = None
    threat_level: Literal["low", "medium", "high", "critical"] = "low"
    mutation_reason: str = Field(default="", max_length=300)
    thought: str = Field(default="", max_length=1000)
    helpfulness_impact: Literal["none", "minor", "significant"] = "none"


class GOATAction(BaseModel):
    role: Literal["red", "blue"]
    red_payload: Optional[RedAction] = None
    blue_payload: Optional[BlueAction] = None


class ConversationTurn(BaseModel):
    turn_number: int
    red_strategy: list[str] = Field(default_factory=list)
    target_response: str = ""
    violation_score: float = Field(ge=0.0, le=1.0)
    blue_prevented: bool = False
    blue_defense: list[str] = Field(default_factory=list)
    novelty_score: float = 0.0


class GOATObservation(BaseModel):
    role: str
    task_id: int
    episode_id: str
    turn_number: int
    max_turns: int
    turns_remaining: int
    conversation_history: list[ConversationTurn]
    current_strategy: list[str]
    current_defense: list[str]
    target_model_profile: str
    registry_size: int
    emergent_count: int
    top_known_strategies: list[dict]
    red_cumulative_reward: float
    blue_cumulative_reward: float
    is_done: bool
    done_reason: Optional[str] = None
    last_violation_score: float = 0.0
    last_novelty_score: float = 0.0
    blue_prevented_last_turn: bool = False
    blue_pattern_correct: bool = False
    over_refusal_count: int = 0


class GOATState(BaseModel):
    episode_id: str
    task_id: int
    turn_number: int
    max_turns: int
    is_done: bool
    done_reason: Optional[str] = None
    red_state: str
    blue_state: str
    total_reward_red: float
    total_reward_blue: float
    registry_size: int
    emergent_count: int


class BattleStartRequest(BaseModel):
    task_id: int = Field(ge=4, le=6)
    model_profile: ModelProfile = ModelProfile.STANDARD
    seed: Optional[int] = None
    red_provider: Literal["huggingface", "nvidia", "openai", "gemini", "scripted"] = "scripted"
    blue_provider: Literal["huggingface", "nvidia", "openai", "gemini", "scripted"] = "scripted"


class VulnerabilityEntry(BaseModel):
    attack_id: str
    name: str
    origin: str
    description: str
    components: list[str]
    known_success_rate: dict[str, float]
    is_emergent: bool
    discovered_at_episode: Optional[str] = None
    novelty_score: Optional[float] = None
    blue_patch_applied: bool = False
    conversation_excerpt: Optional[str] = None
    red_reasoning: Optional[str] = None
    blue_counter_strategy: Optional[list[str]] = None
