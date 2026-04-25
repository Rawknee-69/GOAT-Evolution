from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from backend.agents.blue_agent import BlueAgent
from backend.agents.red_agent import RedAgent
from backend.agents.scripted import ScriptedBlueAgent, ScriptedRedAgent
from backend.core.event_bus import event_bus
from backend.core.models import GOATAction, GOATObservation


@dataclass
class EpisodeResult:
    session_id: str
    winner: str
    score_red: float
    score_blue: float
    registry_delta: int


class CoEvolutionOrchestrator:
    def __init__(self, env: Any, session_id: str):
        self.env = env
        self.session_id = session_id

    async def run_episode(self, use_scripted: bool = True) -> EpisodeResult:
        obs = self.env.reset(task_id=4, episode_id=self.session_id)
        if use_scripted:
            red_agent: Any = ScriptedRedAgent()
            blue_agent: Any = ScriptedBlueAgent()
        else:
            raise RuntimeError("Non-scripted orchestrator path should wire external providers")

        while not obs.is_done:
            red_action = await red_agent.act(obs)
            obs, _, done, _ = self.env.step(GOATAction(role="red", red_payload=red_action))
            if done:
                break
            blue_action = await blue_agent.act(obs)
            obs, _, done, _ = self.env.step(GOATAction(role="blue", blue_payload=blue_action))
            await asyncio.sleep(0)

        event_bus.emit("cycle_episode_done", session_id=self.session_id, winner="red" if obs.red_cumulative_reward >= obs.blue_cumulative_reward else "blue")
        return EpisodeResult(
            session_id=self.session_id,
            winner="red" if obs.red_cumulative_reward >= obs.blue_cumulative_reward else "blue",
            score_red=obs.red_cumulative_reward,
            score_blue=obs.blue_cumulative_reward,
            registry_delta=obs.emergent_count,
        )
