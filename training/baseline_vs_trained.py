"""Baseline-vs-trained evidence generator.

Reads the per-attack reward curve produced by the realtime trainer and the
holdout metrics (baseline + final), and writes:

* ``evidence/summary.json`` - tabular summary judges can copy/paste.
* ``evidence/reward_curve.png`` - reward improvement across attacks (if
  matplotlib is available).
* ``evidence/holdout_compare.png`` - baseline vs final holdout bars.

Designed to run against a finished realtime artifacts directory. Falls back
gracefully if matplotlib isn't installed (writes JSON only).
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


@dataclass
class CurvePoint:
    attack_index: int
    serving_version: int
    violation_score: float
    candidate_violation: float
    baseline_violation: float
    refusal_quality: float
    promoted: bool
    reward_red: float
    reward_blue: float


def _load_curve(path: Path) -> list[CurvePoint]:
    points: list[CurvePoint] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                points.append(
                    CurvePoint(
                        attack_index=int(row["attack_index"]),
                        serving_version=int(row["serving_version"]),
                        violation_score=float(row["violation_score"]),
                        candidate_violation=float(row["candidate_violation"]),
                        baseline_violation=float(row["baseline_violation"]),
                        refusal_quality=float(row["refusal_quality"]),
                        promoted=row["promoted"] == "1",
                        reward_red=float(row["reward_red"]),
                        reward_blue=float(row["reward_blue"]),
                    )
                )
            except Exception:
                continue
    return points


def _summary(points: list[CurvePoint], baseline: dict, final: dict) -> dict:
    if not points:
        return {
            "num_attacks": 0,
            "baseline": baseline,
            "final": final,
            "improvement": {},
        }
    first_third = points[: max(1, len(points) // 3)]
    last_third = points[-max(1, len(points) // 3) :]
    return {
        "num_attacks": len(points),
        "baseline_holdout": baseline,
        "final_holdout": final,
        "violation_avg_first_third": round(mean(p.candidate_violation for p in first_third), 4),
        "violation_avg_last_third": round(mean(p.candidate_violation for p in last_third), 4),
        "refusal_quality_first_third": round(mean(p.refusal_quality for p in first_third), 4),
        "refusal_quality_last_third": round(mean(p.refusal_quality for p in last_third), 4),
        "promotions": sum(1 for p in points if p.promoted),
        "rollbacks": sum(1 for p in points if not p.promoted),
        "reward_red_total": round(sum(p.reward_red for p in points), 4),
        "reward_blue_total": round(sum(p.reward_blue for p in points), 4),
    }


def _maybe_plot(points: list[CurvePoint], baseline: dict, final: dict, out_dir: Path) -> list[str]:
    written: list[str] = []
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return written
    if not points:
        return written

    xs = [p.attack_index for p in points]
    candidate_curve = [p.candidate_violation for p in points]
    baseline_curve = [p.baseline_violation for p in points]
    refusal_curve = [p.refusal_quality for p in points]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, candidate_curve, label="candidate avg violation (lower=better)")
    ax.plot(xs, baseline_curve, label="baseline avg violation", linestyle="--")
    ax.plot(xs, refusal_curve, label="refusal quality (higher=better)")
    ax.set_xlabel("attack index")
    ax.set_ylabel("score")
    ax.set_title("GOAT-Evolution: per-attack training improvement")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    reward_curve_path = out_dir / "reward_curve.png"
    fig.savefig(reward_curve_path, dpi=130)
    plt.close(fig)
    written.append(reward_curve_path.name)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    labels = ["asr", "avg_violation", "refusal_quality"]
    base_vals = [
        baseline.get("asr", 0.0),
        baseline.get("avg_violation", 0.0),
        baseline.get("refusal_quality", 0.0),
    ]
    final_vals = [
        final.get("asr", 0.0),
        final.get("avg_violation", 0.0),
        final.get("refusal_quality", 0.0),
    ]
    x = range(len(labels))
    ax2.bar([i - 0.18 for i in x], base_vals, width=0.36, label="baseline")
    ax2.bar([i + 0.18 for i in x], final_vals, width=0.36, label="trained")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("score")
    ax2.set_title("Baseline vs trained holdout")
    ax2.legend()
    fig2.tight_layout()
    holdout_path = out_dir / "holdout_compare.png"
    fig2.savefig(holdout_path, dpi=130)
    plt.close(fig2)
    written.append(holdout_path.name)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate baseline-vs-trained evidence artifacts."
    )
    parser.add_argument(
        "--artifacts-root",
        default="training/artifacts/realtime",
        help="Realtime trainer artifacts root.",
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Where to write evidence files (defaults to <artifacts-root>/evidence).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.artifacts_root)
    out_dir = Path(args.out_dir) if args.out_dir else root / "evidence"
    out_dir.mkdir(parents=True, exist_ok=True)

    curve_path = root / "reward_curve.csv"
    baseline_path = root / "baseline_holdout.json"
    metrics_path = root / "metrics.json"
    if not curve_path.exists():
        raise FileNotFoundError(f"Missing reward curve at {curve_path}")
    points = _load_curve(curve_path)
    baseline = (
        json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
    )
    metrics = (
        json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    )
    final = metrics.get("baseline_holdout") or baseline
    summary = _summary(points, baseline=baseline, final=final)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    plot_files = _maybe_plot(points, baseline=baseline, final=final, out_dir=out_dir)
    print(f"Wrote evidence summary: {out_dir / 'summary.json'}")
    if plot_files:
        for name in plot_files:
            print(f"Wrote evidence plot: {out_dir / name}")
    else:
        print("matplotlib not available; only JSON summary written.")


if __name__ == "__main__":
    main()
