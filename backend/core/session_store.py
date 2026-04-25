from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class SessionItem:
    value: Any
    expires_at: float


class SessionStore:
    def __init__(self, ttl_seconds: int = 1800):
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, SessionItem] = {}

    def put(self, key: str, value: Any) -> None:
        self._items[key] = SessionItem(value=value, expires_at=time.time() + self.ttl_seconds)

    def get(self, key: str) -> Any | None:
        self.cleanup()
        item = self._items.get(key)
        return item.value if item else None

    def delete(self, key: str) -> None:
        self._items.pop(key, None)

    def cleanup(self) -> None:
        now = time.time()
        expired = [k for k, v in self._items.items() if v.expires_at < now]
        for key in expired:
            self._items.pop(key, None)


session_store = SessionStore()
