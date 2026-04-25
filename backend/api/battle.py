from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, HTTPException

from backend.core.co_evolution import CoEvolutionOrchestrator
from backend.core.session_store import session_store
from backend.server.goat_environment import GoatEnvironment
from backend.core.models import BattleStartRequest

router = APIRouter()


@router.post("/start")
async def start_battle(req: BattleStartRequest):
    session_id = str(uuid.uuid4())
    env = GoatEnvironment()
    env.reset(task_id=req.task_id, episode_id=session_id, model_profile=req.model_profile.value)
    orch = CoEvolutionOrchestrator(env=env, session_id=session_id)
    session_store.put(session_id, {"env": env, "orchestrator": orch, "result": None})
    return {"session_id": session_id, "task_id": req.task_id}


@router.post("/run/{session_id}")
async def run_battle(session_id: str):
    item = session_store.get(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await item["orchestrator"].run_episode(use_scripted=True)
    item["result"] = result
    session_store.put(session_id, item)
    return result.__dict__


@router.get("/state/{session_id}")
async def battle_state(session_id: str):
    item = session_store.get(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    return item["env"].state.model_dump()


@router.get("/result/{session_id}")
async def battle_result(session_id: str):
    item = session_store.get(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    result = item.get("result")
    if not result:
        return {"status": "running"}
    return result.__dict__


@router.post("/stop/{session_id}")
async def stop_battle(session_id: str):
    session_store.delete(session_id)
    return {"status": "stopped", "session_id": session_id}
