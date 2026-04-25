from __future__ import annotations

import os
import time
import uuid
from time import perf_counter

from fastapi import APIRouter, HTTPException

from backend.core.co_evolution import CoEvolutionOrchestrator
from backend.core.hybrid_learning import EpisodeSample, hybrid_learning
from backend.core.session_store import session_store
from backend.server.goat_environment import GoatEnvironment
from backend.core.models import BattleStartRequest

router = APIRouter()


def _parse_env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@router.post("/start")
async def start_battle(req: BattleStartRequest):
    session_id = str(uuid.uuid4())
    env = GoatEnvironment()
    env.reset(task_id=req.task_id, episode_id=session_id, model_profile=req.model_profile.value)
    orch = CoEvolutionOrchestrator(env=env, session_id=session_id)
    serving_version = hybrid_learning.serving_version
    session_store.put(
        session_id,
        {
            "env": env,
            "orchestrator": orch,
            "result": None,
            "task_id": req.task_id,
            "provider": req.red_provider,
            "serving_version": serving_version,
        },
    )
    return {"session_id": session_id, "task_id": req.task_id, "serving_model_version": serving_version}


@router.post("/run/{session_id}")
async def run_battle(session_id: str):
    item = session_store.get(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    started = perf_counter()
    use_scripted = _parse_env_bool("USE_SCRIPTED_MODE", True)
    result = await item["orchestrator"].run_episode(use_scripted=use_scripted)
    item["result"] = result
    session_store.put(session_id, item)
    duration_ms = (perf_counter() - started) * 1000.0
    await hybrid_learning.record_episode(
        EpisodeSample(
            session_id=session_id,
            task_id=item.get("task_id", 4),
            provider=item.get("provider", "scripted"),
            serving_version=item.get("serving_version", 1),
            winner=result.winner,
            score_red=result.score_red,
            score_blue=result.score_blue,
            registry_delta=result.registry_delta,
            duration_ms=duration_ms,
            timestamp=time.time(),
        )
    )
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
