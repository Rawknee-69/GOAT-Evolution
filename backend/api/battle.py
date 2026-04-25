from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.models import GOATAction


def build_battle_router(env) -> APIRouter:
    router = APIRouter(prefix="/api/battle", tags=["battle"])

    @router.post("/start")
    async def start_battle(payload: dict) -> dict:
        task_id = int(payload.get("task_id", 4))
        max_turns = int(payload.get("max_turns", 8))
        obs = await env.reset(task_id=task_id, max_turns=max_turns)
        return {"session_id": obs.session_id, "observation": obs.model_dump()}

    @router.post("/step")
    async def step_battle(payload: dict) -> dict:
        session_id = payload["session_id"]
        action = GOATAction.model_validate(payload["action"])
        try:
            obs = await env.step(action, session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Session not found") from exc
        return {"observation": obs.model_dump()}

    @router.get("/state/{session_id}")
    async def battle_state(session_id: str) -> dict:
        try:
            obs = env.state(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Session not found") from exc
        return obs.model_dump()

    return router
