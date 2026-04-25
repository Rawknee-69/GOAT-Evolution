"""Per-attack training package for the GOAT-Evolution LLM subject.

Modules expose a Python-first pipeline that runs against the OpenEnv-compatible
``GoatEnvironment`` (`reset`, `step`, `state`) without requiring the FastAPI
adapter. The LLM is the test subject; per-attack dataset shards drive
incremental Hugging Face training jobs and gated checkpoint promotion.
"""

from backend.training.gating import GateDecision, HoldoutGate
from backend.training.hf_job_runner import HFJobOutcome, HFJobRunner
from backend.training.judge import AttackJudge, JudgeReport
from backend.training.llm_subject import LLMSubject, SubjectResponse
from backend.training.realtime_dataset import AttackSample, RealtimeDatasetWriter
from backend.training.state import CheckpointLineage, TrainingState

__all__ = [
    "AttackJudge",
    "AttackSample",
    "CheckpointLineage",
    "GateDecision",
    "HFJobOutcome",
    "HFJobRunner",
    "HoldoutGate",
    "JudgeReport",
    "LLMSubject",
    "RealtimeDatasetWriter",
    "SubjectResponse",
    "TrainingState",
]
