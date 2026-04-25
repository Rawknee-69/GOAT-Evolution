from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._channels: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)

    async def publish(self, session_id: str, event: dict[str, Any]) -> None:
        for queue in list(self._channels.get(session_id, [])):
            await queue.put(event)

    async def subscribe_async(self, session_id: str):
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._channels[session_id].append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._channels[session_id].remove(queue)
