from __future__ import annotations

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.event_bus import event_bus

router = APIRouter()


@router.websocket("/ws/battle/{session_id}")
async def battle_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    queue = await event_bus.subscribe(session_id)
    try:
        while True:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30)
                await websocket.send_json(message)
            except asyncio.TimeoutError:
                await websocket.send_json({"event": "ping", "session_id": session_id, "payload": {}})
    except WebSocketDisconnect:
        event_bus.unsubscribe(queue, session_id)
