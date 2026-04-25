"""Centralized structured logging for the GOAT-Evolution training pipeline.

Every CLI invocation creates a new ``logs/run_<utc-stamp>/`` directory with
one file per component plus a combined timeline. All other modules just call
``get_logger("goat.trainer")`` (or one of the shared component names) and
their records land in both the combined log and the per-component log.

Components (logger names):

* ``goat.trainer``  - episode + per-attack orchestration
* ``goat.env``      - GoatEnvironment.reset / step
* ``goat.agents``   - RedAgent / BlueAgent decisions
* ``goat.judge``    - LLMJudge calls + verdicts
* ``goat.subject``  - LLMSubject responses + per-attack updates
* ``goat.hfjob``    - HFJobRunner lifecycle
* ``goat.gate``     - HoldoutGate evaluations + promotion decisions

Records use a JSON suffix on the formatter so files double as machine-readable
event logs while remaining human-friendly.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


COMPONENT_LOGGERS = (
    "goat.trainer",
    "goat.env",
    "goat.agents",
    "goat.judge",
    "goat.subject",
    "goat.hfjob",
    "goat.gate",
)


_RUN_DIR: Path | None = None
_INITIALIZED = False


def get_logger(name: str) -> logging.Logger:
    """Return a logger; idempotent and safe to call before setup."""
    return logging.getLogger(name)


def current_run_dir() -> Path | None:
    return _RUN_DIR


def setup_logging(
    logs_root: Path | str = "logs",
    run_label: str | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> Path:
    """Configure logging for the current process. Returns the run directory."""
    global _RUN_DIR, _INITIALIZED
    if _INITIALIZED and _RUN_DIR is not None:
        return _RUN_DIR

    logs_root_path = Path(logs_root)
    logs_root_path.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = run_label or os.getenv("GOAT_RUN_LABEL") or f"run_{stamp}"
    run_dir = logs_root_path / label
    run_dir.mkdir(parents=True, exist_ok=True)
    _RUN_DIR = run_dir

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    root = logging.getLogger("goat")
    root.setLevel(file_level)
    root.handlers.clear()

    combined_handler = logging.FileHandler(run_dir / "all.log", encoding="utf-8")
    combined_handler.setLevel(file_level)
    combined_handler.setFormatter(fmt)
    root.addHandler(combined_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(fmt)
    root.addHandler(console_handler)

    for name in COMPONENT_LOGGERS:
        logger = logging.getLogger(name)
        logger.setLevel(file_level)
        logger.propagate = True
        component_path = run_dir / f"{name.split('.')[-1]}.log"
        handler = logging.FileHandler(component_path, encoding="utf-8")
        handler.setLevel(file_level)
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    manifest = {
        "label": label,
        "started_at": time.time(),
        "logs_root": str(logs_root_path.resolve()),
        "run_dir": str(run_dir.resolve()),
        "components": list(COMPONENT_LOGGERS),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _INITIALIZED = True
    get_logger("goat.trainer").info(
        json.dumps({"event": "logging_initialized", "run_dir": str(run_dir)})
    )
    return run_dir


def log_event(logger_name: str, event: str, **fields: Any) -> None:
    """Helper to emit a structured event line."""
    payload = {"event": event}
    for key, value in fields.items():
        payload[key] = _safe_json(value)
    get_logger(logger_name).info(json.dumps(payload, default=str))


def _safe_json(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_safe_json(v) for v in value]
    return str(value)
