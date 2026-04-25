"""Persisted training state.

Tracks serving / candidate / last-good checkpoint labels and per-attack
lineage so the trainer can promote, rollback, and resume across runs.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class CheckpointLineage:
    label: str
    parent_label: str | None
    created_at: float
    promoted: bool
    metrics: dict[str, float] = field(default_factory=dict)
    sample_id: str | None = None
    serving_version: int = 1


@dataclass
class TrainingState:
    serving_label: str = "v1-base"
    last_good_label: str = "v1-base"
    candidate_label: str | None = None
    serving_version: int = 1
    total_attacks: int = 0
    total_breaking: int = 0
    total_promotions: int = 0
    total_rollbacks: int = 0
    history: list[CheckpointLineage] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "serving_label": self.serving_label,
            "last_good_label": self.last_good_label,
            "candidate_label": self.candidate_label,
            "serving_version": self.serving_version,
            "total_attacks": self.total_attacks,
            "total_breaking": self.total_breaking,
            "total_promotions": self.total_promotions,
            "total_rollbacks": self.total_rollbacks,
            "history": [asdict(item) for item in self.history],
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "TrainingState":
        history = [
            CheckpointLineage(**item) for item in raw.get("history", []) if isinstance(item, dict)
        ]
        return cls(
            serving_label=raw.get("serving_label", "v1-base"),
            last_good_label=raw.get("last_good_label", "v1-base"),
            candidate_label=raw.get("candidate_label"),
            serving_version=int(raw.get("serving_version", 1)),
            total_attacks=int(raw.get("total_attacks", 0)),
            total_breaking=int(raw.get("total_breaking", 0)),
            total_promotions=int(raw.get("total_promotions", 0)),
            total_rollbacks=int(raw.get("total_rollbacks", 0)),
            history=history,
            updated_at=float(raw.get("updated_at", time.time())),
        )


class TrainingStateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load()

    def _load(self) -> TrainingState:
        if not self.path.exists():
            initial = TrainingState()
            self._write(initial)
            return initial
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return TrainingState.from_dict(data)
        except Exception:
            return TrainingState()

    def _write(self, state: TrainingState) -> None:
        state.updated_at = time.time()
        self.path.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")

    def record_attack(self, *, breaking: bool) -> None:
        self.state.total_attacks += 1
        if breaking:
            self.state.total_breaking += 1
        self._write(self.state)

    def register_candidate(
        self,
        *,
        label: str,
        parent_label: str,
        metrics: dict[str, float],
        sample_id: str | None,
    ) -> CheckpointLineage:
        lineage = CheckpointLineage(
            label=label,
            parent_label=parent_label,
            created_at=time.time(),
            promoted=False,
            metrics=metrics,
            sample_id=sample_id,
            serving_version=self.state.serving_version,
        )
        self.state.candidate_label = label
        self.state.history.append(lineage)
        self._write(self.state)
        return lineage

    def promote_candidate(self, *, metrics: dict[str, float]) -> None:
        if not self.state.candidate_label:
            return
        self.state.last_good_label = self.state.serving_label
        self.state.serving_label = self.state.candidate_label
        self.state.serving_version += 1
        self.state.total_promotions += 1
        if self.state.history:
            self.state.history[-1].promoted = True
            self.state.history[-1].metrics = metrics
            self.state.history[-1].serving_version = self.state.serving_version
        self.state.candidate_label = None
        self._write(self.state)

    def rollback_candidate(self, *, reason: str) -> None:
        self.state.total_rollbacks += 1
        if self.state.history:
            self.state.history[-1].promoted = False
            self.state.history[-1].metrics["rollback_reason"] = reason  # type: ignore[index]
        self.state.candidate_label = None
        self._write(self.state)
