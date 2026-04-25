"""Thin wrapper that exposes ``training/baseline_vs_trained.py`` as a console
script. Keeps the heavy logic next to the other training scripts so judges can
inspect it from one place, while still letting users run it via
``uv run goat-evidence``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "training" / "baseline_vs_trained.py"
    if not script_path.exists():
        raise FileNotFoundError(
            f"Expected training script at {script_path}; check repository layout."
        )
    spec = importlib.util.spec_from_file_location(
        "training_baseline_vs_trained", script_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = _load_module()
    module.main()


if __name__ == "__main__":
    main()
