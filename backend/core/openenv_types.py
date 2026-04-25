from __future__ import annotations

from typing import TYPE_CHECKING, Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from openenv.core.env_server.types import Action as ActionBase
    from openenv.core.env_server.types import Observation as ObservationBase
    from openenv.core.env_server.types import State as StateBase
else:
    try:
        from openenv.core.env_server.types import Action as ActionBase
        from openenv.core.env_server.types import Observation as ObservationBase
        from openenv.core.env_server.types import State as StateBase
    except Exception:  # pragma: no cover
        class ActionBase(BaseModel):
            model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
            metadata: dict[str, Any] = Field(default_factory=dict)

        class ObservationBase(BaseModel):
            model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
            done: bool = False
            reward: bool | int | float | None = None
            metadata: dict[str, Any] = Field(default_factory=dict)

        class StateBase(BaseModel):
            model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
            episode_id: str | None = None
            step_count: int = 0


class GoatAction(ActionBase):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    role: Literal["red", "blue"]
    action_json: str


class GoatObservation(ObservationBase):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    payload_json: str


class GoatState(StateBase):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    payload_json: str
