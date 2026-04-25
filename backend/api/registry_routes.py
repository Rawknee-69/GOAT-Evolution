from __future__ import annotations

from fastapi import APIRouter


def build_registry_router(registry) -> APIRouter:
    router = APIRouter(prefix="/api/registry", tags=["registry"])

    @router.get("")
    async def all_entries() -> list[dict]:
        return registry.get_all()

    @router.get("/emergent")
    async def emergent_entries() -> list[dict]:
        return registry.get_emergent()

    return router
