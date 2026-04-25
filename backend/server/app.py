from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import baseline, battle, metrics, registry, websocket

try:
    from openenv.core.env_server.http_server import create_app as create_openenv_app
except Exception:
    create_openenv_app = None

from backend.core.openenv_types import GoatAction, GoatObservation
from backend.server.goat_environment import GoatEnvironment

FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

if create_openenv_app:
    app: FastAPI = create_openenv_app(GoatEnvironment, GoatAction, GoatObservation, env_name="goat_evolution", max_concurrent_envs=8)
else:
    app = FastAPI(title="goat_evolution")


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "goat_evolution"}


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> dict:
    try:
        body = await request.json()
    except Exception:
        body = {}
    method = body.get("method", "")
    rid = body.get("id", 1)
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "tools": [
                    {
                        "name": "deploy_attack_strategy",
                        "description": "Deploy ordered attack components for Red",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["red"]},
                                "strategy": {"type": "array", "items": {"type": "string"}},
                                "thought": {"type": "string"},
                            },
                            "required": ["role", "strategy", "thought"],
                        },
                    },
                    {
                        "name": "deploy_defense",
                        "description": "Deploy defense components for Blue",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["blue"]},
                                "defense": {"type": "array", "items": {"type": "string"}},
                                "thought": {"type": "string"},
                            },
                            "required": ["role", "defense", "thought"],
                        },
                    },
                ]
            },
        }
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}


app.include_router(battle.router, prefix="/api/battle", tags=["Battle"])
app.include_router(registry.router, prefix="/api/registry", tags=["Registry"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(baseline.router, prefix="/api/baseline", tags=["Baseline"])
app.include_router(websocket.router, tags=["WebSocket"])

if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str = ""):
        skip = ("api/", "health", "reset", "step", "state", "ws", "mcp", "web")
        if any(full_path.startswith(p) for p in skip):
            return JSONResponse({"error": "Not found"}, status_code=404)
        return FileResponse(FRONTEND_DIST / "index.html")
