from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

try:
    from openenv.core.env_server.types import Action, Observation, State
except Exception:  # pragma: no cover
    @dataclass
    class Action:  # type: ignore[no-redef]
        pass

    @dataclass
    class Observation:  # type: ignore[no-redef]
        pass

    @dataclass
    class State:  # type: ignore[no-redef]
        pass


@dataclass
class GoatAction(Action):
    role: Literal["red", "blue"]
    action_json: str


@dataclass
class GoatObservation(Observation):
    payload_json: str


@dataclass
class GoatState(State):
    payload_json: str
