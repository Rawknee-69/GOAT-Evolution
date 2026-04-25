from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket
from sse_starlette import EventSourceResponse


def build_stream_router(event_bus) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/battle/{session_id}")
    async def battle_ws(websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        async for event in event_bus.subscribe_async(session_id):
            await websocket.send_text(json.dumps(event))

    @router.get("/sse/battle/{session_id}")
    async def battle_sse(session_id: str) -> EventSourceResponse:
        async def _events():
            async for event in event_bus.subscribe_async(session_id):
                yield {"event": event.get("type", "message"), "data": json.dumps(event)}

        return EventSourceResponse(_events())

    return router
