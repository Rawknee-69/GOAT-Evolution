from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(os.getenv("REGISTRY_PATH", "backend/data/vulnerability_registry.json"))


def _levenshtein(a: list[str], b: list[str]) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        prev = dp[0]
        dp[0] = i
        for j, cb in enumerate(b, start=1):
            curr = dp[j]
            if ca == cb:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = curr
    return dp[-1]


class VulnerabilityRegistry:
    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = path
        self._lock = threading.Lock()
        self._data: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")
        self._data = json.loads(self.path.read_text())

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2))

    def get_all(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._data)

    def get_emergent(self) -> list[dict[str, Any]]:
        with self._lock:
            return [x for x in self._data if x.get("is_emergent")]

    def get_by_profile(self, profile: str) -> list[dict[str, Any]]:
        with self._lock:
            return [x for x in self._data if profile in x.get("known_success_rate", {})]

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {
                "total_entries": len(self._data),
                "emergent_count": len([x for x in self._data if x.get("is_emergent")]),
            }

    def compute_novelty_score(self, components: list[str]) -> float:
        with self._lock:
            existing = [x.get("components", []) for x in self._data]
        if not existing:
            return 1.0
        distances = [_levenshtein(components, c) for c in existing]
        max_len = max(max(len(components), max(len(c) for c in existing)), 1)
        min_dist = min(distances)
        return round(min(1.0, min_dist / max_len), 3)

    def maybe_add_emergent(
        self,
        components: list[str],
        success_rate: dict[str, float],
        episode_id: str,
        red_reasoning: str,
        conversation_excerpt: str,
        blue_counter: list[str],
    ) -> str | None:
        novelty = self.compute_novelty_score(components)
        if novelty < 0.45:
            return None
        with self._lock:
            attack_id = f"emergent_{len(self._data) + 1:03d}"
            entry = {
                "attack_id": attack_id,
                "name": f"Emergent attack {attack_id}",
                "origin": "goat_evolution",
                "description": "Auto-discovered during self-play",
                "components": components,
                "known_success_rate": success_rate,
                "is_emergent": True,
                "discovered_at_episode": episode_id,
                "novelty_score": novelty,
                "blue_patch_applied": False,
                "conversation_excerpt": conversation_excerpt,
                "red_reasoning": red_reasoning,
                "blue_counter_strategy": blue_counter,
            }
            self._data.append(entry)
            self._save()
            return attack_id


registry = VulnerabilityRegistry()
