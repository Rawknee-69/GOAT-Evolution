from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JudgeVerdict:
    violation_score: float
    response_type: str
    was_defended: bool


class DeterministicJudge:
    def evaluate(self, response: dict) -> JudgeVerdict:
        return JudgeVerdict(
            violation_score=float(response.get("violation_score", 0.0)),
            response_type=str(response.get("response_type", "refuse")),
            was_defended=bool(response.get("was_defended", False)),
        )
