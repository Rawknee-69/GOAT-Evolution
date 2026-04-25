---
title: GOAT-Evolution
emoji: ⚔️
colorFrom: red
colorTo: blue
sdk: docker
app_port: 7860
tags:
  - openenv
  - reinforcement-learning
  - ai-safety
  - self-improvement
  - multi-agent
license: mit
---

# GOAT-Evolution ⚔️

GOAT-Evolution is an OpenEnv-compatible multi-agent safety training environment where:

- **Red agent** tries to discover jailbreak strategies.
- **Blue agent** tries to stop them with layered defenses.
- **Judge + trainer** convert each attack into learning data and run continual improvement with promotion/rollback gates.

This project is built specifically for OpenEnv Hackathon judging: runnable Space, runnable Colab training, and explicit reward-improvement artifacts.

---

## TL;DR for Judges

- **OpenEnv latest**: supported (`openenv.yaml`, `/reset`, `/step`, `/state`).
- **HF Space deployable**: Docker Space + helper script.
- **Training notebooks**:
  - TRL: `training/trl_colab_finetune.ipynb`
  - Unsloth: `training/unsloth_finetune.ipynb`
  - End-to-end online loop: `training/colab_training.ipynb`
- **Evidence outputs**: `summary.json`, `reward_curve.png`, `holdout_compare.png`.
- **Theme fit**: Multi-agent interactions + long-horizon + world modeling + self-improvement.

> Add your final public links before submission:
>
> - Hugging Face Space: `<SPACE_URL>`
> - Hugging Face mini-blog: `<HF_BLOG_URL>`
> - Demo video (<2 min): `<YOUTUBE_URL>`

---

## Problem Statement

Current LLM hardening often evaluates static prompts offline. GOAT-Evolution instead trains a defender in a **live adversarial loop** where attacks mutate over time and defenses must adapt across turns. The goal is to improve real-world robustness against emergent jailbreak behaviors, not just benchmark memorization.

---

## Hackathon Theme Mapping

### Theme #1 - Multi-Agent Interactions

- Red and Blue are explicit competing agents with different incentives.
- Blue can defend input and output guardrail layers independently.
- Red chooses target layer and strategy composition to exploit Blue mistakes.

### Theme #2 - Long-Horizon Planning & Instruction Following

- Episodes are multi-turn trajectories with delayed outcomes.
- Red/Blue adaptation across turns requires state tracking and strategic sequencing.
- Promotion decisions depend on holdout behavior, not one-step reward spikes.

### Theme #3 - World Modeling (Professional Tasks)

- The environment simulates a realistic layered safety stack:
  - input filtering,
  - model generation,
  - output filtering.
- Agents must reason about hidden internal state (what got blocked where).

### Theme #4 - Self-Improvement

- Every attack can trigger a training step, candidate checkpoint, and gate decision.
- Model versions are promoted/rolled back automatically based on quality/safety signals.

### Theme #5 - Wild Card potential

- The same architecture can be extended to negotiation, enterprise workflow safety, or personalized assistant conflict handling by swapping task generators and rubrics.

---

## How the Environment Works

### Core Environment

- Canonical env: `backend/server/goat_environment.py`
- Gym-style API:
  - `reset(seed, episode_id, task_id, model_profile) -> GOATObservation`
  - `step(action) -> (GOATObservation, reward, done, info)`
  - `state -> GOATState`

### OpenEnv HTTP Compatibility

- Adapter: `backend/server/openenv_adapter.py`
- OpenEnv server app: `backend/server/app.py`
- Exposes `/reset`, `/step`, `/state`, `/health`, `/metadata`, `/schema`.
- Adapter converts gym tuple outputs into OpenEnv-compliant observation payloads with `reward` and `done`.

### Two-Layer Safety Model

Red attack flow:

1. Prompt enters **input guardrail**
2. If passed, model drafts response
3. Draft enters **output guardrail**
4. Final response is emitted or blocked

Blue gets higher reward for stopping attacks earlier (input layer), encouraging practical cost-aware defenses.

---

## Reward Design (What is Being Learned)

Implemented in `backend/core/reward.py`.

- Red is rewarded for:
  - successful violations,
  - bypassing input guardrails,
  - exploiting undefended targeted layers,
  - novelty.
- Blue is rewarded for:
  - input-layer blocks (highest),
  - output-layer blocks,
  - defending both layers,
  - and penalized for leaks/open layers.

This creates a richer signal than binary success/fail and is harder to game than single scalar endpoints.

---

## Training Pipeline

Online loop entrypoint: `backend/cli/realtime_trainer.py`

Per-attack cycle:

1. Collect attack/response trace from env
2. Grade with judge
3. Write JSONL shard
4. Run local update (`stub` policy or `hf_local` LoRA step)
5. Evaluate holdout gate
6. Promote or rollback candidate

Supporting modules:

- Subject model wrapper: `backend/training/llm_subject.py`
- HF job orchestration: `backend/training/hf_job_runner.py`
- Holdout gate: `backend/training/gating.py`
- Dataset writer: `backend/training/realtime_dataset.py`
- Training state lineage: `backend/training/state.py`

---

## Reproducible Training Options (Judge Requirement)

### Option A: Minimal local smoke

```bash
uv sync
uv run goat-realtime-train --episodes 3 --task-id 4 --subject-size 3b --backend stub
uv run goat-evidence --artifacts-root training/artifacts/realtime
```

### Option B: TRL in Colab

- Notebook: `training/trl_colab_finetune.ipynb`
- Script: `training/hf_online_finetune.py`

### Option C: Unsloth in Colab

- Notebook: `training/unsloth_finetune.ipynb`

All notebooks support scripted fallback for data generation if external keys are not set.

---

## Evidence and Metrics (Judge Requirement)

Generated by `training/baseline_vs_trained.py`:

- `evidence/summary.json`
- `evidence/reward_curve.png`
- `evidence/holdout_compare.png`

Expected interpretation:

- lower violation / ASR over time,
- stable or improved refusal quality,
- visible baseline vs trained gap on holdout suite.

Keep these artifacts committed and linked in submission materials.

---

## Hugging Face Space Deployment

1. Create Docker Space.
2. Set secrets:
   - required: `HF_TOKEN`
   - optional providers: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `NVIDIA_API_KEY`
3. Deploy:

```bash
bash scripts/deploy_hf_space.sh <hf-username> <space-name>
```

4. Smoke test OpenEnv HTTP:

```bash
curl https://<hf-username>-<space-name>.hf.space/health
curl https://<hf-username>-<space-name>.hf.space/metadata
```

Judge helper notebook:

- `training/openenv_space_smoke.ipynb`

---

## Submission Checklist (Minimum Requirements)

- [x] Uses OpenEnv latest API surface
- [x] OpenEnv-compliant environment hosted on HF Space
- [x] Minimal training path with TRL or Unsloth in Colab
- [x] Reward improvement evidence artifacts
- [ ] HF mini-blog URL added
- [ ] <2 minute YouTube demo URL added
- [ ] Final Space URL added

---

## Project Structure

```text
backend/
  api/                         # battle, registry, metrics, websocket routes
  core/                        # models, reward, simulator, registry, orchestrators
  server/                      # OpenEnv app, adapter, canonical GoatEnvironment
  training/                    # subject, judge, gating, HF jobs, state
  cli/                         # realtime trainer + evidence wrappers
training/
  colab_training.ipynb         # end-to-end online loop notebook
  trl_colab_finetune.ipynb     # TRL fine-tuning notebook
  unsloth_finetune.ipynb       # Unsloth fine-tuning notebook
  baseline_vs_trained.py       # reward and holdout plot generation
openenv.yaml                   # OpenEnv Space manifest
scripts/deploy_hf_space.sh     # one-command HF Space push
```

---

## Validation Commands

```bash
uv run pytest backend/tests
uv run goat-realtime-train --episodes 2 --backend stub --artifacts-root /tmp/goat_smoke
uv run goat-evidence --artifacts-root /tmp/goat_smoke
```

If you need a narrative architecture walkthrough, see `SYSTEM_EXPLAINED.md`.
