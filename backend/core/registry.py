from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from Levenshtein import distance as levenshtein_distance

from backend.core.models import AttackComponent, VulnerabilityEntry


class VulnerabilityRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[VulnerabilityEntry]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [VulnerabilityEntry.model_validate(item) for item in raw]

    def _save(self, entries: list[VulnerabilityEntry]) -> None:
        self.path.write_text(
            json.dumps([entry.model_dump() for entry in entries], indent=2),
            encoding="utf-8",
        )

    def snapshot(self) -> list[VulnerabilityEntry]:
        with self._lock:
            return self._load()

    def compute_novelty_score(self, components: list[AttackComponent]) -> float:
        current = ",".join(c.value for c in components)
        with self._lock:
            entries = self._load()
        if not entries:
            return 1.0
        distances = []
        for entry in entries:
            other = ",".join(c.value for c in entry.components)
            distances.append(levenshtein_distance(current, other))
        max_dist = max(distances) if distances else 0
        return min(1.0, max_dist / max(len(current), 1))

    def maybe_add_emergent(self, components: list[AttackComponent], target_model: str, novelty_threshold: float = 0.4) -> VulnerabilityEntry | None:
        novelty = self.compute_novelty_score(components)
        if novelty < novelty_threshold:
            return None
        with self._lock:
            entries = self._load()
            attack_id = f"emergent_{len(entries)+1:03d}"
            entry = VulnerabilityEntry(
                attack_id=attack_id,
                components=components,
                target_model=target_model,
                novelty_score=novelty,
                discovered_at=datetime.now(timezone.utc).isoformat(),
            )
            entries.append(entry)
            self._save(entries)
        return entry
