from __future__ import annotations

import uuid

from backend.core.event_bus import EventBus
from backend.core.models import (
    AttackComponent,
    DefenseComponent,
    GOATAction,
    GOATObservation,
    GOATState,
    ConversationTurn,
    ModelProfile,
)
from backend.core.registry import VulnerabilityRegistry
from backend.core.reward import compute_rewards
from backend.core.target_simulator import TargetModelSimulator


class GOATEvolutionEnvironment:
    def __init__(self, registry: VulnerabilityRegistry, event_bus: EventBus) -> None:
        self.registry = registry
        self.event_bus = event_bus
        self.simulator = TargetModelSimulator()
        self.sessions: dict[str, GOATState] = {}

    async def reset(self, task_id: int = 4, max_turns: int = 8, session_id: str | None = None) -> GOATObservation:
        sid = session_id or str(uuid.uuid4())
        state = GOATState(session_id=sid, task_id=task_id, max_turns=max_turns)
        self.sessions[sid] = state
        await self.event_bus.publish(sid, {"type": "battle_started", "session_id": sid})
        return self._obs(state)

    async def step(self, action: GOATAction, session_id: str) -> GOATObservation:
        state = self.sessions[session_id]
        if state.done:
            return self._obs(state)

        if action.role == "red" and action.red_payload:
            attack = action.red_payload.strategy
            defense = self._latest_defense(state)
            await self.event_bus.publish(session_id, {"type": "red_deploys", "strategy": [a.value for a in attack]})
        elif action.role == "blue" and action.blue_payload:
            attack = self._latest_attack(state)
            defense = action.blue_payload.defense
            await self.event_bus.publish(session_id, {"type": "blue_deploys", "defense": [d.value for d in defense]})
        else:
            attack = self._latest_attack(state)
            defense = self._latest_defense(state)

        state.turn += 1
        violation, response_type, response_text = self.simulator.respond(
            attack_components=attack,
            defense_components=defense,
            profile=ModelProfile.STANDARD,
            turn=state.turn,
            max_turns=state.max_turns,
        )
        novelty = self.registry.compute_novelty_score(attack)
        red_reward, blue_reward = compute_rewards(violation, novelty, state.turn, state.max_turns)
        state.cumulative_red_reward += red_reward
        state.cumulative_blue_reward += blue_reward
        turn = ConversationTurn(
            turn_index=state.turn,
            red_strategy=attack,
            blue_defense=defense,
            target_response=response_text,
            violation_score=violation,
        )
        state.history.append(turn)
        await self.event_bus.publish(
            session_id,
            {"type": "target_responds", "response_type": response_type, "violation_score": violation, "text": response_text},
        )

        entry = self.registry.maybe_add_emergent(attack, "simulator")
        if entry:
            await self.event_bus.publish(session_id, {"type": "registry_entry_added", "attack_id": entry.attack_id})

        if state.turn >= state.max_turns:
            state.done = True
            await self.event_bus.publish(
                session_id,
                {"type": "episode_ended", "red_reward": state.cumulative_red_reward, "blue_reward": state.cumulative_blue_reward},
            )
        return self._obs(state)

    def state(self, session_id: str) -> GOATObservation:
        return self._obs(self.sessions[session_id])

    def _obs(self, state: GOATState) -> GOATObservation:
        return GOATObservation(
            session_id=state.session_id,
            task_id=state.task_id,
            turn=state.turn,
            max_turns=state.max_turns,
            history=state.history,
            cumulative_red_reward=state.cumulative_red_reward,
            cumulative_blue_reward=state.cumulative_blue_reward,
            done=state.done,
        )

    @staticmethod
    def _latest_attack(state: GOATState) -> list[AttackComponent]:
        if not state.history:
            return [AttackComponent.CRESCENDO, AttackComponent.DETAIL_ESCALATION]
        return state.history[-1].red_strategy

    @staticmethod
    def _latest_defense(state: GOATState) -> list[DefenseComponent]:
        if not state.history:
            return [DefenseComponent.EARLY_INTERVENTION]
        return state.history[-1].blue_defense
