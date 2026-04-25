from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.registry import registry

router = APIRouter()


@router.get("")
async def list_registry():
    return registry.get_all()


@router.get("/emergent")
async def emergent_registry():
    return registry.get_emergent()


@router.get("/{attack_id}")
async def get_entry(attack_id: str):
    for entry in registry.get_all():
        if entry.get("attack_id") == attack_id:
            return entry
    raise HTTPException(status_code=404, detail="Entry not found")
