from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api.battle import router as battle_router
from backend.api.openenv_routes import build_openenv_router
from backend.api.registry_routes import build_registry_router
from backend.api.websocket import router as websocket_router
from backend.core.registry import registry

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

app = FastAPI(title="GOAT-Evolution")
app.include_router(build_openenv_router())
app.include_router(battle_router, prefix="/api/battle", tags=["Battle"])
app.include_router(build_registry_router(registry))
app.include_router(websocket_router)

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    root = full_path.split("/", 1)[0] if full_path else ""
    if root in {"health", "metadata", "schema", "tasks"}:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    if full_path.startswith(("api/", "docs", "ws/", "redoc")) or full_path == "openapi.json":
        return JSONResponse({"detail": "Not found"}, status_code=404)
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "GOAT-Evolution backend running", "path": full_path}
