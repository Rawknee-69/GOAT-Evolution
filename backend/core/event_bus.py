from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._channels: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def emit(self, event: str, session_id: str, **payload: Any) -> None:
        message = {"event": event, "session_id": session_id, "payload": payload}
        for key in (session_id, "*"):
            for queue in list(self._channels.get(key, [])):
                queue.put_nowait(message)

    async def subscribe(self, session_id: str = "*") -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._channels[session_id].append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue, session_id: str = "*") -> None:
        if session_id in self._channels and queue in self._channels[session_id]:
            self._channels[session_id].remove(queue)


event_bus = EventBus()
