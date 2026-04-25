from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.battle import build_battle_router
from backend.api.openenv_routes import build_openenv_router
from backend.api.registry_routes import build_registry_router
from backend.api.websocket import build_stream_router
from backend.core.event_bus import EventBus
from backend.core.registry import VulnerabilityRegistry
from backend.environment.goat_mcp_env import GOATEvolutionEnvironment

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
REGISTRY_PATH = BASE_DIR / "backend" / "data" / "vulnerability_registry.json"

registry = VulnerabilityRegistry(REGISTRY_PATH)
event_bus = EventBus()
env = GOATEvolutionEnvironment(registry=registry, event_bus=event_bus)

app = FastAPI(title="GOAT-Evolution")
app.include_router(build_openenv_router())
app.include_router(build_battle_router(env))
app.include_router(build_registry_router(registry))
app.include_router(build_stream_router(event_bus))

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "GOAT-Evolution backend running", "path": full_path}
