from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def baseline_scores():
    return {"task_4": 0.42, "task_5_red": 0.30, "task_6_cycle": 0.38}
