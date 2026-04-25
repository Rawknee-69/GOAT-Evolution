from __future__ import annotations

from fastapi import APIRouter


def build_registry_router(registry) -> APIRouter:
    router = APIRouter(prefix="/api/registry", tags=["registry"])

    @router.get("")
    async def all_entries() -> list[dict]:
        return [entry.model_dump() for entry in registry.snapshot()]

    @router.get("/emergent")
    async def emergent_entries() -> list[dict]:
        return [entry.model_dump() for entry in registry.snapshot() if entry.attack_id.startswith("emergent_")]

    return router
