"""Hugging Face TRL fine-tuner for the GOAT-Evolution LLM subject.

Consumes the per-attack JSONL dataset produced by the realtime trainer
(`backend.cli.realtime_trainer`) and runs an SFT step over the supervised
"chosen_response" column. Designed to be:

* Idempotent: takes a sample-id offset so subsequent runs only train on new
  shards.
* Resumable: continues from a previously saved adapter directory.
* Colab-friendly: small footprint, uses TRL's ``SFTTrainer`` + PEFT/LoRA.

Push the resulting adapter to Hugging Face for serving / further compute.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TrainingConfig:
    dataset_jsonl: Path
    base_model: str
    output_dir: Path
    resume_adapter: Path | None
    push_to_hub: bool
    hub_model_id: str | None
    epochs: int
    batch_size: int
    grad_accum: int
    learning_rate: float
    max_length: int
    only_breaking: bool
    since_sample_id: str | None
    use_lora: bool
    lora_r: int
    lora_alpha: int
    lora_dropout: float


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows.append(json.loads(stripped))
    return rows


def _filter_rows(
    rows: list[dict[str, Any]],
    only_breaking: bool,
    since_sample_id: str | None,
) -> list[dict[str, Any]]:
    if since_sample_id:
        seen = False
        kept: list[dict[str, Any]] = []
        for row in rows:
            if not seen:
                if str(row.get("sample_id")) == since_sample_id:
                    seen = True
                continue
            kept.append(row)
        rows = kept
    if only_breaking:
        rows = [r for r in rows if bool(r.get("is_breaking"))]
    return rows


def _format_text(row: dict[str, Any]) -> str:
    prompt = str(row.get("prompt", ""))
    chosen = str(row.get("chosen_response", ""))
    return f"<|user|>\n{prompt}\n<|assistant|>\n{chosen}"


def parse_args() -> TrainingConfig:
    parser = argparse.ArgumentParser(
        description="TRL SFT fine-tune from per-attack GOAT-Evolution shards."
    )
    parser.add_argument("--dataset-jsonl", required=True)
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--output-dir", default="training/artifacts/hf-finetuned")
    parser.add_argument("--resume-adapter", default="")
    parser.add_argument("--push-to-hub", action="store_true")
    parser.add_argument("--hub-model-id", default="")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=768)
    parser.add_argument("--only-breaking", action="store_true")
    parser.add_argument("--since-sample-id", default="")
    parser.add_argument("--no-lora", action="store_true")
    parser.add_argument("--lora-r", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    args = parser.parse_args()
    return TrainingConfig(
        dataset_jsonl=Path(args.dataset_jsonl),
        base_model=args.base_model,
        output_dir=Path(args.output_dir),
        resume_adapter=Path(args.resume_adapter) if args.resume_adapter else None,
        push_to_hub=bool(args.push_to_hub),
        hub_model_id=args.hub_model_id or None,
        epochs=int(args.epochs),
        batch_size=int(args.batch_size),
        grad_accum=int(args.grad_accum),
        learning_rate=float(args.learning_rate),
        max_length=int(args.max_length),
        only_breaking=bool(args.only_breaking),
        since_sample_id=args.since_sample_id or None,
        use_lora=not bool(args.no_lora),
        lora_r=int(args.lora_r),
        lora_alpha=int(args.lora_alpha),
        lora_dropout=float(args.lora_dropout),
    )


def main() -> None:
    cfg = parse_args()
    if not cfg.dataset_jsonl.exists():
        raise FileNotFoundError(f"Dataset not found: {cfg.dataset_jsonl}")
    if cfg.push_to_hub:
        if not cfg.hub_model_id:
            raise RuntimeError("--hub-model-id is required when --push-to-hub is used")
        if not os.getenv("HF_TOKEN"):
            raise RuntimeError("HF_TOKEN is required to push to Hugging Face")

    rows = _filter_rows(
        _load_jsonl(cfg.dataset_jsonl),
        only_breaking=cfg.only_breaking,
        since_sample_id=cfg.since_sample_id,
    )
    if not rows:
        raise RuntimeError(
            "No samples to train on. Run the realtime trainer or relax filters."
        )

    import torch
    from datasets import Dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(cfg.base_model, torch_dtype=dtype)

    if cfg.use_lora:
        from peft import LoraConfig, TaskType, get_peft_model

        lora = LoraConfig(
            r=cfg.lora_r,
            lora_alpha=cfg.lora_alpha,
            lora_dropout=cfg.lora_dropout,
            target_modules=["q_proj", "v_proj"],
            task_type=TaskType.CAUSAL_LM,
        )
        model = get_peft_model(model, lora)

    if cfg.resume_adapter and cfg.resume_adapter.exists():
        try:
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, str(cfg.resume_adapter), is_trainable=True)
        except Exception:
            pass

    formatted = [{"text": _format_text(row)} for row in rows]
    dataset = Dataset.from_list(formatted)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    training_args = SFTConfig(
        output_dir=str(cfg.output_dir),
        num_train_epochs=cfg.epochs,
        per_device_train_batch_size=cfg.batch_size,
        gradient_accumulation_steps=cfg.grad_accum,
        learning_rate=cfg.learning_rate,
        max_length=cfg.max_length,
        logging_steps=5,
        save_steps=50,
        save_total_limit=2,
        bf16=torch.cuda.is_available(),
        report_to=[],
        push_to_hub=cfg.push_to_hub,
        hub_model_id=cfg.hub_model_id or None,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    train_result = trainer.train()
    trainer.save_model(str(cfg.output_dir))
    tokenizer.save_pretrained(str(cfg.output_dir))
    metrics_path = cfg.output_dir / "train_metrics.json"
    metrics_payload = {
        "train_runtime": getattr(train_result, "metrics", {}).get("train_runtime"),
        "train_loss": getattr(train_result, "metrics", {}).get("train_loss"),
        "rows_used": len(rows),
        "base_model": cfg.base_model,
        "use_lora": cfg.use_lora,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    if cfg.push_to_hub:
        trainer.push_to_hub(cfg.hub_model_id)
        tokenizer.push_to_hub(cfg.hub_model_id)
        print(f"Pushed model: https://huggingface.co/{cfg.hub_model_id}")
    print(f"Saved checkpoint: {cfg.output_dir}")


if __name__ == "__main__":
    main()
