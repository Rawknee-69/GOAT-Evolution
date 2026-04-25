from __future__ import annotations

from fastapi import APIRouter


def build_openenv_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    @router.get("/metadata")
    async def metadata() -> dict[str, str]:
        return {
            "name": "goat-evolution",
            "version": "0.1.0",
            "description": "Co-evolution safety environment",
        }

    @router.get("/schema")
    async def schema() -> dict[str, str]:
        return {"action_type": "GOATAction", "observation_type": "GOATObservation"}

    @router.get("/tasks")
    async def tasks() -> list[dict[str, int | str]]:
        return [
            {"id": 4, "name": "Medium Co-evolution", "difficulty": "medium", "max_steps": 8},
            {"id": 5, "name": "Hard Co-evolution", "difficulty": "hard", "max_steps": 8},
            {"id": 6, "name": "Expert Co-evolution", "difficulty": "expert", "max_steps": 10},
        ]

    return router
