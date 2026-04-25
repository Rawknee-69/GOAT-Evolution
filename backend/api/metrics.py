from __future__ import annotations

from fastapi import APIRouter

from backend.core.hybrid_learning import hybrid_learning
from backend.core.registry import registry

router = APIRouter()


@router.get("")
async def metrics():
    snap = registry.snapshot()
    learning = await hybrid_learning.snapshot()
    return {
        "registry_size": snap["total_entries"],
        "emergent_attacks": snap["emergent_count"],
        "hybrid_learning": learning,
    }


@router.post("/rollback")
async def rollback_serving_model():
    return await hybrid_learning.rollback()
