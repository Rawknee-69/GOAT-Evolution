from __future__ import annotations

from fastapi import APIRouter

from backend.core.registry import registry

router = APIRouter()


@router.get("")
async def metrics():
    snap = registry.snapshot()
    return {
        "registry_size": snap["total_entries"],
        "emergent_attacks": snap["emergent_count"],
    }
