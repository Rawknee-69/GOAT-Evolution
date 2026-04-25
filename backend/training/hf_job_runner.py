"""Per-attack Hugging Face training job runner.

Each attack triggers a discrete training job:

1. Build a candidate label.
2. Apply an in-process LoRA/policy update on the subject (the work HF would
   do remotely).
3. Persist the candidate checkpoint locally.
4. Optionally upload the per-attack shard + candidate checkpoint to the
   configured Hugging Face dataset and model repos so a remote job can pick
   up exactly where the local run stopped.
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from backend.training.llm_subject import LLMSubject
from backend.training.logging_setup import log_event
from backend.training.realtime_dataset import AttackSample


@dataclass
class HFJobOutcome:
    job_id: str
    candidate_label: str
    parent_label: str
    sample_id: str
    serving_version: int
    ran_remote: bool
    ran_local: bool
    update: dict[str, Any]
    started_at: float
    finished_at: float
    push_results: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HFJobRunner:
    """Orchestrates a single per-attack training job."""

    def __init__(
        self,
        subject: LLMSubject,
        artifacts_root: Path,
        hf_dataset_repo: str | None = None,
        hf_model_repo: str | None = None,
        push_each_attack: bool = False,
    ) -> None:
        self.subject = subject
        self.artifacts_root = artifacts_root
        self.artifacts_root.mkdir(parents=True, exist_ok=True)
        self.hf_dataset_repo = hf_dataset_repo
        self.hf_model_repo = hf_model_repo
        self.push_each_attack = push_each_attack
        self._hf_api: Any = None

    def _hf_client(self) -> Any:
        if self._hf_api is not None:
            return self._hf_api
        token = os.getenv("HF_TOKEN")
        if not token:
            return None
        try:
            from huggingface_hub import HfApi

            self._hf_api = HfApi(token=token)
            return self._hf_api
        except Exception:
            return None

    def run(
        self,
        sample: AttackSample,
        shard_path: Path,
        parent_label: str,
        serving_version: int,
    ) -> HFJobOutcome:
        started = time.time()
        candidate_label = self._mint_candidate_label(serving_version, sample)
        log_event(
            "goat.hfjob",
            "job_started",
            sample_id=sample.sample_id,
            candidate_label=candidate_label,
            parent_label=parent_label,
            shard=str(shard_path),
            push_each_attack=self.push_each_attack,
            hf_dataset_repo=self.hf_dataset_repo,
            hf_model_repo=self.hf_model_repo,
        )
        update = self.subject.apply_update(
            {
                "prompt": sample.prompt,
                "chosen_response": sample.chosen_response,
                "rejected_response": sample.rejected_response,
                "blue_defense": sample.blue_defense,
                "violation_score": sample.violation_score,
                "novelty_score": sample.novelty_score,
                "blue_prevented": sample.blue_prevented,
            }
        )
        checkpoint_dir = self.subject.save_checkpoint(candidate_label)
        push_results: dict[str, Any] = {}
        ran_remote = False
        if self.push_each_attack:
            log_event(
                "goat.hfjob",
                "remote_push_start",
                sample_id=sample.sample_id,
                candidate_label=candidate_label,
            )
            push_results = self._push_to_hub(
                shard_path=shard_path,
                checkpoint_dir=checkpoint_dir,
                candidate_label=candidate_label,
                sample=sample,
            )
            ran_remote = bool(push_results.get("dataset") or push_results.get("model"))
            log_event(
                "goat.hfjob",
                "remote_push_done",
                sample_id=sample.sample_id,
                candidate_label=candidate_label,
                push_results=push_results,
                ran_remote=ran_remote,
            )
        finished = time.time()
        job_id = f"job_{candidate_label}"
        return HFJobOutcome(
            job_id=job_id,
            candidate_label=candidate_label,
            parent_label=parent_label,
            sample_id=sample.sample_id,
            serving_version=serving_version,
            ran_remote=ran_remote,
            ran_local=True,
            update=update,
            started_at=started,
            finished_at=finished,
            push_results=push_results,
        )

    def _mint_candidate_label(self, serving_version: int, sample: AttackSample) -> str:
        return f"v{serving_version + 1}-attack{sample.attack_index:04d}-{sample.sample_id[-8:]}"

    def _push_to_hub(
        self,
        shard_path: Path,
        checkpoint_dir: Path,
        candidate_label: str,
        sample: AttackSample,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {"dataset": None, "model": None, "errors": []}
        api = self._hf_client()
        if api is None:
            result["errors"].append("HF_TOKEN_missing_or_huggingface_hub_unavailable")
            return result
        if self.hf_dataset_repo:
            try:
                api.create_repo(
                    repo_id=self.hf_dataset_repo,
                    private=True,
                    repo_type="dataset",
                    exist_ok=True,
                )
                api.upload_file(
                    path_or_fileobj=str(shard_path),
                    path_in_repo=f"shards/{shard_path.name}",
                    repo_id=self.hf_dataset_repo,
                    repo_type="dataset",
                    commit_message=f"Attack shard {sample.sample_id}",
                )
                result["dataset"] = {
                    "repo": self.hf_dataset_repo,
                    "path": f"shards/{shard_path.name}",
                }
            except Exception as exc:
                result["errors"].append(f"dataset_push_failed:{exc}")
        if self.hf_model_repo:
            try:
                api.create_repo(
                    repo_id=self.hf_model_repo,
                    private=True,
                    repo_type="model",
                    exist_ok=True,
                )
                api.upload_folder(
                    folder_path=str(checkpoint_dir),
                    path_in_repo=f"checkpoints/{candidate_label}",
                    repo_id=self.hf_model_repo,
                    repo_type="model",
                    commit_message=f"Candidate checkpoint {candidate_label}",
                )
                result["model"] = {
                    "repo": self.hf_model_repo,
                    "path": f"checkpoints/{candidate_label}",
                }
            except Exception as exc:
                result["errors"].append(f"model_push_failed:{exc}")
        return result
