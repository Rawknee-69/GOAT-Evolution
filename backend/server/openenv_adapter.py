"""OpenEnv-compliant adapter for ``GoatEnvironment``.

OpenEnv expects ``reset(...) -> Observation`` and ``step(action) -> Observation``
where the returned Observation carries ``reward``, ``done``, and ``metadata``
fields directly. The internal :class:`GoatEnvironment` exposes a Gym-style
``(obs, reward, done, info)`` tuple from ``step`` so the realtime trainer can
keep using the well-known API.

This adapter wraps the Gym-style env and produces a Pydantic Observation that
satisfies OpenEnv's contract while still containing every GOAT field a judge
might want to inspect over HTTP.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ConfigDict, Field

from backend.core.models import GOATAction, GOATObservation
from backend.server.goat_environment import GoatEnvironment

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import Action, Observation


class GOATOpenEnvAction(Action):
    """OpenEnv action carrier for GOAT.

    Pydantic v2 with ``extra='forbid'`` is too strict for nested unions in JSON
    transport, so the canonical action is sent as a JSON string in
    ``action_json`` and parsed into :class:`GOATAction` server-side. The
    ``role`` field is duplicated for quick inspection.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    role: str = Field(default="red", description="Acting role: 'red' or 'blue'")
    action_json: str = Field(default="{}", description="JSON-encoded GOATAction payload")


class GOATOpenEnvObservation(Observation):
    """Flat OpenEnv observation that mirrors :class:`GOATObservation`.

    All GOAT fields are exposed at the top level so judges/clients can inspect
    them without parsing nested JSON. ``reward``, ``done``, and ``metadata`` are
    inherited from :class:`Observation`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    role: str = "red"
    task_id: int = 0
    episode_id: str = ""
    turn_number: int = 0
    max_turns: int = 0
    turns_remaining: int = 0
    target_model_profile: str = ""
    registry_size: int = 0
    emergent_count: int = 0
    red_cumulative_reward: float = 0.0
    blue_cumulative_reward: float = 0.0
    is_done: bool = False
    done_reason: str | None = None
    last_violation_score: float = 0.0
    last_input_violation_score: float = 0.0
    last_output_violation_score: float = 0.0
    last_novelty_score: float = 0.0
    blue_prevented_last_turn: bool = False
    blue_input_blocked_last_turn: bool = False
    blue_output_blocked_last_turn: bool = False
    last_caught_at_layer: str | None = None
    current_strategy: list[str] = Field(default_factory=list)
    current_input_defense: list[str] = Field(default_factory=list)
    current_output_defense: list[str] = Field(default_factory=list)
    conversation_history_json: str = "[]"
    top_known_strategies_json: str = "[]"


def _obs_to_openenv(obs: GOATObservation, *, reward: float, done: bool, info: dict[str, Any] | None) -> GOATOpenEnvObservation:
    return GOATOpenEnvObservation(
        done=done,
        reward=float(reward),
        metadata=dict(info or {}),
        role=obs.role,
        task_id=obs.task_id,
        episode_id=obs.episode_id,
        turn_number=obs.turn_number,
        max_turns=obs.max_turns,
        turns_remaining=obs.turns_remaining,
        target_model_profile=obs.target_model_profile,
        registry_size=obs.registry_size,
        emergent_count=obs.emergent_count,
        red_cumulative_reward=obs.red_cumulative_reward,
        blue_cumulative_reward=obs.blue_cumulative_reward,
        is_done=obs.is_done,
        done_reason=obs.done_reason,
        last_violation_score=obs.last_violation_score,
        last_input_violation_score=obs.last_input_violation_score,
        last_output_violation_score=obs.last_output_violation_score,
        last_novelty_score=obs.last_novelty_score,
        blue_prevented_last_turn=obs.blue_prevented_last_turn,
        blue_input_blocked_last_turn=obs.blue_input_blocked_last_turn,
        blue_output_blocked_last_turn=obs.blue_output_blocked_last_turn,
        last_caught_at_layer=(
            obs.last_caught_at_layer.value if obs.last_caught_at_layer else None
        ),
        current_strategy=list(obs.current_strategy),
        current_input_defense=list(obs.current_input_defense),
        current_output_defense=list(obs.current_output_defense),
        conversation_history_json=json.dumps(
            [t.model_dump(mode="json") for t in obs.conversation_history]
        ),
        top_known_strategies_json=json.dumps(obs.top_known_strategies),
    )


class GOATOpenEnvEnvironment(Environment):
    """OpenEnv wrapper that delegates to the Gym-style ``GoatEnvironment``.

    Methods follow OpenEnv's single-Observation return contract:
        reset(...) -> GOATOpenEnvObservation
        step(action) -> GOATOpenEnvObservation
    """

    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self) -> None:
        self._env = GoatEnvironment()

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: int = 4,
        model_profile: str = "standard_model",
        **_: Any,
    ) -> GOATOpenEnvObservation:
        obs = self._env.reset(
            seed=seed,
            episode_id=episode_id,
            task_id=task_id,
            model_profile=model_profile,
        )
        return _obs_to_openenv(obs, reward=0.0, done=False, info={"phase": "reset"})

    def step(self, action: GOATOpenEnvAction) -> GOATOpenEnvObservation:
        try:
            payload = json.loads(action.action_json or "{}")
        except json.JSONDecodeError:
            payload = {}
        if "role" not in payload and getattr(action, "role", None):
            payload["role"] = action.role
        goat_action = GOATAction.model_validate(payload)
        obs, reward, done, info = self._env.step(goat_action)
        return _obs_to_openenv(obs, reward=reward, done=done, info=info)

    @property
    def state(self) -> Any:
        return self._env.state

    def close(self) -> None:
        return None
