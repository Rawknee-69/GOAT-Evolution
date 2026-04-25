from __future__ import annotations

import uuid

from backend.core.event_bus import EventBus
from backend.core.models import (
    GOATAction,
    GOATObservation,
)
from backend.core.registry import VulnerabilityRegistry
from backend.server.goat_environment import GoatEnvironment


class GOATEvolutionEnvironment:
    """Session-oriented wrapper over the canonical GoatEnvironment.

    This adapter keeps the legacy MCP-facing interface (`reset`, `step`, `state`
    with explicit `session_id`) while delegating all battle logic to
    `backend.server.goat_environment.GoatEnvironment`.
    """

    def __init__(self, registry: VulnerabilityRegistry, event_bus: EventBus) -> None:
        self.registry = registry
        self.event_bus = event_bus
        self.sessions: dict[str, GoatEnvironment] = {}

    async def reset(
        self,
        task_id: int = 4,
        max_turns: int = 8,
        session_id: str | None = None,
    ) -> GOATObservation:
        # `max_turns` is accepted for backward compatibility with older callers.
        # Canonical max-turn behavior is controlled internally by GoatEnvironment
        # from task_id/profile.
        _ = max_turns
        sid = session_id or str(uuid.uuid4())
        env = GoatEnvironment()
        self.sessions[sid] = env
        obs = env.reset(task_id=task_id, episode_id=sid, model_profile="standard_model")
        self.event_bus.emit("battle_started", session_id=sid, task_id=task_id)
        return obs

    async def step(self, action: GOATAction, session_id: str) -> GOATObservation:
        env = self._require_session(session_id)
        obs, reward, done, info = env.step(action)
        self.event_bus.emit(
            "mcp_step",
            session_id=session_id,
            role=action.role,
            reward=float(reward),
            done=bool(done),
            info=info,
        )
        return obs

    def state(self, session_id: str) -> GOATObservation:
        env = self._require_session(session_id)
        return env._build_observation("observer")  # type: ignore[attr-defined]

    def _require_session(self, session_id: str) -> GoatEnvironment:
        env = self.sessions.get(session_id)
        if env is None:
            raise KeyError(f"Unknown session_id: {session_id}")
        return env
